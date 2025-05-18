from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from app.schema.chat import ChatRequest, ChatResponse
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from app.db.base import engine
from app.settings import settings
from app.utils.faiss_utils import search_faiss_index
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.med_record_processor import ask_gemini_about_medicine
import os

router = APIRouter(prefix="/chat", tags=["chat"])

db = SQLDatabase(engine)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", google_api_key=settings.GENAI_API_KEY
)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest = Body(...)):
    try:
        # Use FAISS vector search to get top relevant posts
        top_k = 10
        results = search_faiss_index(request.message, k=top_k)
        posts_text = ""
        if not results:
            # fallback: no index or no results, use all posts (legacy)
            from app.db.db_schema import Post as PostModel
            from sqlalchemy.orm import Session
            from app.db.base import SessionLocal

            db_session: Session = SessionLocal()
            posts = db_session.query(PostModel).all()
            posts_text = "\n".join([f"- {p.text}" for p in posts if p.text])
            db_session.close()
        else:
            posts_text = "\n".join([f"- {text}" for text, _ in results if text])

        # If patient_username is provided, extract medical PDF text
        pdf_text = ""
        if request.patient_username:
            pdf_path = os.path.join(
                "static", request.patient_username, "Medical_Record.pdf"
            )
            pdf_text = extract_text_from_pdf(pdf_path)

        # Compose prompt
        if pdf_text:
            prompt = (
                "Here is the patient's medical record (PDF):\n"
                f"{pdf_text}\n\n"
                "Here are the most relevant messages posted by users as context for your answer:\n"
                f"{posts_text}\n\n"
                f"User question: {request.message}\n"
                "Answer based on the above medical record and messages."
            )
        else:
            prompt = (
                "Here are the most relevant messages posted by users as context for your answer:\n"
                f"{posts_text}\n\n"
                f"User question: {request.message}\n"
                "Answer based on the above messages."
            )
        result = llm.invoke(prompt)
        return ChatResponse(response=result.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask-medicine", response_model=ChatResponse)
def ask_medicine(patient_username: str = Body(...), file: UploadFile = File(...)):
    try:
        image_bytes = file.file.read()
        answer = ask_gemini_about_medicine(image_bytes, patient_username)
        return ChatResponse(response=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
