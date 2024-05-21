from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv, environ
from bunnet import init_bunnet


from models.app_model import App
from models.order_model import Order
from models.user_model import User

load_dotenv(override=True)

class TuMongo:

    def __init__(self) -> None:
        db = "tutrader"
        url = getenv("MONGO_URL_LOCAL") if environ["ENV"] == 'dev' else getenv("MONGO_URL")
        print(url)
        self.client = MongoClient(url)
        init_bunnet(database=self.client[db], document_models=[App, Order, User])
        print("MONGO INITIALIZED")


