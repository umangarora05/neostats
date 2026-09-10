from pymongo import MongoClient
from .config import settings

# In MongoDB, the connection string typically includes the database name
# or we can append it. Atlas strings usually look like:
# mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority

from pymongo.errors import ConfigurationError

client = MongoClient(settings.DATABASE_URL)

try:
    db = client.get_default_database()
except ConfigurationError:
    db = client['neostats']

def get_db():
    """
    Yields the MongoDB database instance.
    """
    yield db
