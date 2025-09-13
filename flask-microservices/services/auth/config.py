import os
from dotenv import load_dotenv
stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)

class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret')
    AUTH_SECRET = os.environ.get('AUTH_SECRET', 'default-secret')
    EXTERNAL_BASE = os.environ.get('EXTERNAL_BASE', 'https://dummyjson.com')
    PORT = int(os.environ.get('PORT', 5000))
    DATABASE_URL = os.environ.get('DATABASE_URL')
