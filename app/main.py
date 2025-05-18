from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.settings import settings
import importlib
import pkgutil
import os
import cloudinary

app = FastAPI(debug=settings.DEBUG, title="Backend for CogniMed", version="1.0.0")

api_v1_path = os.path.join(os.path.dirname(__file__), "api", "v1")
package_name = "app.api.v1"

for _, module_name, _ in pkgutil.iter_modules([api_v1_path]):
    module = importlib.import_module(f"{package_name}.{module_name}")
    if hasattr(module, "router"):
        app.include_router(module.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static")),
    name="static",
)

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)
