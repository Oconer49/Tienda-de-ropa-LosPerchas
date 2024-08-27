from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("LosPerchas_API_KEY")

uri = f"mongodb+srv://darenaslop3z:{api_key}@cluster0.xaevb.mongodb.net/"

connection = MongoClient(uri, server_api=ServerApi('1'))

try:
    connection.admin.command('ping')
    database = connection["Inventory"]
    print("Conexion exitosa a la base de datos")
except Exception as e:
    print(e)