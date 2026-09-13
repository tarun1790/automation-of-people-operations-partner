import os
from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "workforce.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Hardware acceleration setup
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CUDA_AVAILABLE = torch.cuda.is_available()
GPU_NAME = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"

APP_NAME = "TalentOS AI - Intelligent Workforce Management Platform"
APP_VERSION = "2.4.0"
API_PREFIX = "/api/v1"

# Academic & Organizational Framework Settings
FRAMEWORK_META = {
    "foundational_paper": "The Importance of Human Resources (HR) Management in Company",
    "lead_author": "Lia Marthalia (2022)",
    "publication": "Journal of World Science, Vol 1 No. 9, pp. 700-705",
    "primary_functions": [
        "Staffing & Employment",
        "Performance Evaluation",
        "Compensation & Benefits",
        "Training & Development",
        "Employee Relations",
        "Safety & Health",
        "Personnel Research & Analytics"
    ]
}
