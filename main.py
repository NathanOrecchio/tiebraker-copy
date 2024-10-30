# Imports

from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import errors
from logging import info
from routes import router as event_router
from database import db

config = dotenv_values(".env")
URI = config.get("DB_URI")
DEFAULT_DB = config.get("DB_NAME")

# Establishing Database Connection on Startup and closing connection on Shutdown.
async def db_lifespan(app : FastAPI):

    # Startup
    try:
        db.connect_to_database(URI=URI, DEFAULT_DB=DEFAULT_DB)
        print("Connected to database successfully.")

    except errors.ConnectionFailure as err:
        print(f"Error connecting to database {err}")
    except errors.PyMongoError as err:
        print(f"General Mongo error occured: {err}")

    yield

    # Shutdown
    db.close_database_connection()

    
app : FastAPI = FastAPI(lifespan=db_lifespan)

# Registering endpoints
app.include_router(event_router)


