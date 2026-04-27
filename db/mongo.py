from pymongo import MongoClient
from config.settings import MONGODB_URI, DB_NAME
import certifi

# client = MongoClient(MONGODB_URI)
client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    tlsCAFile=certifi.where()
)

db = client[DB_NAME]