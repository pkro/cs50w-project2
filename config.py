import os

debug = os.getenv("FLASK_DEBUG") == "1"

secret_key = os.getenv("SECRET_KEY")