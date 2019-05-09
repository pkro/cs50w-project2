import os

secret_key = os.getenv("SECRET_KEY")
debug = os.getenv("FLASK_DEBUG") == "1"