from dotenv import load_dotenv

from app.db.database import import_models

load_dotenv()
import_models()
