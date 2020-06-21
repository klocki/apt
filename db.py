import pymongo
import datetime
from scraper import get_asin

cluster = pymongo.MongoClient('mongodb+srv://klchristoph:AltMOair1988Cluster0@cluster0-k0phs.mongodb.net/test?retryWrites=true&w=majority')
db = cluster["amazon"]

def add_product_detail(details):
    new = db["products"]
    ASIN = get_asin(details)
    details["date"] = datetime.datetime.now()
    try:
        new.update_one(
            {
                "asin":ASIN
            }, 
            {
                "$set": {
                    "asin":ASIN
                }, 
                "$push":{
                    "details":details
                }
            }, 
            upsert=True
        )
        return True
    except Exception as identifier:
        print(identifier)
        return False


def get_product_history(asin):
    new = db["products"]
    try:
        find = new.find_one({"asin": asin}) #, {"_id": 0})
        if find:
            return find
    except Exception as identifier:
        print(identifier)
        return None