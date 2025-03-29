import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///code_analyzer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up temp directory for cloned repositories
app.config["REPO_TEMP_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_repos")
if not os.path.exists(app.config["REPO_TEMP_DIR"]):
    os.makedirs(app.config["REPO_TEMP_DIR"])

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import the models here
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)

logger.info("Application initialized successfully")
