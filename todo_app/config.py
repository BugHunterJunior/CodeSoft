import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DATABASE = os.path.join(BASE_DIR, "todo.db")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
