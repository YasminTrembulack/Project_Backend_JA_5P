from dotenv import load_dotenv

load_dotenv()

from app import main  # noqa: F401, E402
from app.db.database import import_models  # noqa: E402

import_models()
