import google.generativeai as genai
from app.settings import settings
import sys
import os
import json
import re
import datetime
from fpdf import FPDF
import PyPDF2
import requests
from app.utils.pdf_utils import extract_text_from_pdf

genai.configure(api_key=settings.GENAI_API_KEY)


class PDFGenerator:
    """Generates a structured PDF from text data."""

    def __init__(self, output_path):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        self.output_path = output_path

    def add_section(self, title, content):
        """Adds a section to the PDF with a title and content."""
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(200, 10, title, ln=True, align="L")
        self.pdf.ln(4)
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0, 10, content)
        self.pdf.ln(5)

    def save_pdf(self):
        """Saves the PDF to the specified path."""
        self.pdf.output(self.output_path)
        print(f"PDF saved to {self.output_path}")


def process_medical_image(image_bytes):
    """Extract structured text and notification data from medical image using Gemini."""
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Image data is empty. Please provide a valid image.")
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(
            [
                "Extract medical record in two parts:\n"
                "PART 1: Structured text format with:\n"
                "1. Patient Information: Name, Age, Gender\n"
                "2. Medical History: Conditions, Medications, Allergies\n"
                "3. Vitals: Blood Pressure, Heart Rate, Temperature\n"
                "4. Lab Results: Blood Tests, Urinalysis, Imaging Results etc.. \n"
                "5. If a data is not available, leave it and don't mention about that data at all.\n"
                "6. If any additional data is given extract that and mention it in the report.\n"
                "7. Doctor's Notes: Diagnosis, Recommendations\n\n"
                "PART 2: JSON format for notifications (inside ```json markers):\n"
                "- Extract prescription details including:\n"
                "  - Medicine names\n"
                "  - Dosage instructions\n"
                "  - Intake times with boolean flags for:\n"
                "    - morning\n"
                "    - afternoon\n"
                "    - evening\n"
                "    - night\n"
                "  - Duration (in days/weeks/months)\n"
                "- Extract follow-up information:\n"
                "  - Next doctor visit date (YYYY-MM-DD format)\n"
                "  - Reason for follow-up\n"
                "- If no prescription found, return empty arrays\n"
                "Example format:\n"
                "```json\n"
                "{\n"
                '  "patient_info": {"name": "John Doe", "age": 35, "gender": "male"},\n'
                '  "medications": [\n'
                "    {\n"
                '      "name": "Paracetamol",\n'
                '      "dosage": "500mg",\n'
                '      "morning": "yes",\n'
                '      "afternoon": "no",\n'
                '      "evening": "yes",\n'
                '      "night": "no",\n'
                '      "duration": "7 days",\n'
                '      "instructions": "Take after meals"\n'
                "    },\n"
                "    {\n"
                '      "name": "Amoxicillin",\n'
                '      "dosage": "250mg",\n'
                '      "morning": "yes",\n'
                '      "afternoon": "yes",\n'
                '      "evening": "yes",\n'
                '      "night": "no",\n'
                '      "duration": "10 days",\n'
                '      "instructions": "Take with plenty of water"\n'
                "    }\n"
                "  ],\n"
                '  "next_visit": {\n'
                '    "date": "2024-03-15",\n'
                '    "reason": "Follow-up checkup"\n'
                "  }\n"
                "}\n"
                "```",
                {"mime_type": "image/jpeg", "data": image_bytes},
            ],
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 4096,
            },
        )
        return response.text

    except Exception as e:
        print(f"Error during image processing: {str(e)}")
        raise


def extract_notification_json(text):
    """Extract JSON data from response text using markdown markers."""
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if not match:
            return None

        json_str = match.group(1)
        json_data = json.loads(json_str)

        # Validate JSON structure
        required_keys = ["patient_info", "medications", "next_visit"]
        for key in required_keys:
            if key not in json_data:
                print(f"Missing key in JSON data: {key}")
                return None

        return json_data

    except json.JSONDecodeError:
        print("Invalid JSON format in response")
        return None
    except Exception as e:
        print(f"Error extracting JSON data: {str(e)}")
        return None


def save_notification_data(json_data, output_dir):
    """Save or update notification data in JSON file with timestamp."""
    try:
        output_path = os.path.join(output_dir, "medical_notifications.json")
        current_time = datetime.datetime.now().isoformat()

        # Create notification entry
        notification_entry = {
            "processing_time": current_time,
            "patient_info": json_data.get("patient_info", {}),
            "medications": json_data.get("medications", []),
            "next_visit": json_data.get("next_visit", {}),
        }

        # Read existing data or initialize new list
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Append new entry
        existing_data.append(notification_entry)

        # Save updated data
        with open(output_path, "w") as f:
            json.dump(existing_data, f, indent=2)

        print(f"Notification data updated at {output_path}")

    except Exception as e:
        print(f"Error saving notification data: {str(e)}")


def extract_med_info_save(image_bytes, username):
    try:
        print("Processing medical record...")

        response_text = process_medical_image(image_bytes)
        output_dir = os.getcwd()  # Use current working directory for output
        output_dir = os.path.join(output_dir, "static", username)
        os.makedirs(output_dir, exist_ok=True)

        # Split response into structured text and JSON data
        structured_text = response_text.split("```json")[0].strip()
        json_data = extract_notification_json(response_text)

        # Handle PDF generation
        output_pdf_path = os.path.join(output_dir, "Medical_Record.pdf")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        section_title = f"Extracted Medical Record ({current_time})"

        if os.path.exists(output_pdf_path):
            # Create temporary PDF with new content
            temp_pdf_path = os.path.join(output_dir, "TEMP_MEDICAL_RECORD.pdf")
            pdf_gen = PDFGenerator(temp_pdf_path)
            pdf_gen.add_section(section_title, structured_text)
            pdf_gen.save_pdf()

            # Merge with existing PDF
            merger = PyPDF2.PdfMerger()
            merger.append(output_pdf_path)
            merger.append(temp_pdf_path)
            merger.write(output_pdf_path)
            merger.close()

            # Cleanup temporary file
            os.remove(temp_pdf_path)
            print(f"Updated existing PDF at {output_pdf_path}")
        else:
            # Create new PDF
            pdf_gen = PDFGenerator(output_pdf_path)
            pdf_gen.add_section(section_title, structured_text)
            pdf_gen.save_pdf()

        # Handle JSON notifications
        if json_data:
            save_notification_data(json_data, output_dir)
            print("Successfully saved medication tracking data")
        else:
            print("No medication or follow-up data found in document")
    except Exception as e:
        print(f"Error: {str(e)}")


def get_image(url: str) -> bytes | None:
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error downloading image: {str(e)}")
        return None


def ask_gemini_about_medicine(image_bytes: bytes, patient_username: str) -> str:
    """
    Passes an image of a pill/tablet, patient's Medical_Record.pdf, and medical_notifications.json to Gemini,
    and asks about the name, purpose, and reason for use of the medicine in the image.
    """
    # Paths to patient files
    static_dir = os.path.join("static", patient_username)
    pdf_path = os.path.join(static_dir, "Medical_Record.pdf")
    json_path = os.path.join(static_dir, "medical_notifications.json")

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Load JSON data
    json_text = ""
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            json_text = f.read()

    # Compose prompt
    prompt = (
        "You are a medical assistant. Given the following documents and an image of a pill or tablet, "
        "answer these questions:\n"
        "1. What is the name of the medicine shown in the image?\n"
        "2. What is the purpose of that particular medicine?\n"
        "3. Why does the patient have to use it specifically?\n"
        "4. How much dosage should I take?\n"
        "5. Which time of the day should I take it?\n"
        "\n---\n"
        f"Patient's Medical Record (PDF):\n{pdf_text}\n\n"
        f"Patient's Medical Notifications (JSON):\n{json_text}\n\n"
        "Please answer using only the information from the provided documents and the image."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
    )
    return response.text
