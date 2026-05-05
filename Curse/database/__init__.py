from sys import exit as exiter

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, InvalidURI, PyMongoError
from pymongo.uri_parser import parse_uri

from Curse import DB_NAME, DB_URI, LOGGER


def _redact_mongo_uri(uri):
    if not uri:
        return "<empty>"
    uri = str(uri)
    if "@" not in uri:
        return uri[:32] + ("..." if len(uri) > 32 else "")
    prefix, host = uri.rsplit("@", 1)
    scheme = prefix.split("://", 1)[0] if "://" in prefix else "mongodb"
    return f"{scheme}://<credentials>@{host[:32]}{'...' if len(host) > 32 else ''}"


def _validate_mongo_uri(uri):
    if not uri:
        raise InvalidURI("DB_URI is empty")
    if uri in {"mongodb://", "mongodb+srv://"} or "..." in uri:
        raise InvalidURI("DB_URI looks like a placeholder, not a full MongoDB URI")
    if not uri.startswith(("mongodb://", "mongodb+srv://")):
        raise InvalidURI("DB_URI must start with mongodb:// or mongodb+srv://")
    parse_uri(uri)


try:
    _validate_mongo_uri(DB_URI)
    Curse_db_client = MongoClient(
        DB_URI,
        connectTimeoutMS=10000,
        serverSelectionTimeoutMS=10000,
    )
    Curse_db_client.admin.command("ping")
except (ConfigurationError, InvalidURI, PyMongoError, UnicodeError) as f:
    LOGGER.error(
        "MongoDB connection failed. Set Railway DB_URI to the full MongoDB connection string, not a placeholder."
    )
    LOGGER.error("Current DB_URI value starts as: %s", _redact_mongo_uri(DB_URI))
    LOGGER.error("MongoDB error: %s", f)
    exiter(1)
Curse_main_db = Curse_db_client[DB_NAME]


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self.collection = Curse_main_db[collection]

    # Insert one entry into collection
    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    # Count entries from collection
    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    # Replace one entry in collection
    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return Curse_db_client.close()


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()
