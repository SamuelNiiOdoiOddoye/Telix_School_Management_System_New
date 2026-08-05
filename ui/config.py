from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
DATA_DIR = PROJECT_DIR

TELIX_ICON_PATH = IMAGES_DIR / "telix_image.ico"
ICON_PATH = TELIX_ICON_PATH

STUDENT_FILE = DATA_DIR / "student_records.json"
TEACHER_FILE = DATA_DIR / "teacher_records.json"
ACADEMIC_FILE = DATA_DIR / "academic_records.json"
