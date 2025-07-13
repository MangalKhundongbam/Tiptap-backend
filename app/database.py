import motor.motor_asyncio # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI","mongodb://127.0.0.1:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["Demo"]
