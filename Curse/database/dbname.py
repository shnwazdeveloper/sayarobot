from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from Curse import BDB_URI, DB_NAME

mongo = MongoClient(BDB_URI)
dbname = mongo[DB_NAME]
