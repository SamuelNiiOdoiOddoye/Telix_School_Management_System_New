from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

TELIX_ICON_PATH = IMAGES_DIR / "telix_image.ico"
TELIX_ICON_IMAGE_PATH = IMAGES_DIR / "telix_image.png"

STUDENT_FILE = PROJECT_DIR / "student_records.json"
TEACHER_FILE = PROJECT_DIR / "teacher_records.json"
ACADEMIC_FILE = PROJECT_DIR / "academic_records.json"
