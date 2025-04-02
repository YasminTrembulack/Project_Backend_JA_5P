from dotenv import load_dotenv  # noqa: I001

load_dotenv()

from app.db.database import import_models  # noqa: E402, I001

import_models()
