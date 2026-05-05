from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from Curse import BDB_URI

mongo = MongoClient(BDB_URI)
dbname = mongo.SukunaDb
