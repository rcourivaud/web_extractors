import json

from pymongo import MongoClient

from webextractors.archi.receiver import Receiver


class ScraperReceiver(Receiver):
    def __init__(self):
        super().__init__("scraper")

        self.client = MongoClient('localhost', 27017)

        self.all_receiver = {"leboncoin": ["annonces", "leboncoinOffers2402"],
                             "logicimmo": ["annonces", "logicImmoOffers"],
                             "meilleursagents": ["prices", "MeilleursAgentsRoads"]}

    def callback(self, ch, method, properties, body):
        print("Receive messgae")
        message = json.loads(body.decode('utf-8'))
        print(message)
        offers = message.get("offers")
        which = message.get("which")
        print("Write on mongo")
        for offer in offers:
            try:
                self.insert_to_mongo(offer=offer, which=which)
            except Exception as e:
                pass

    def insert_to_mongo(self, offer, which):
        params = self.all_receiver[which]
        print(params)
        inserted_id = self.client[params[0]][params[1]].insert_one(offer).inserted_id


if __name__ == "__main__":
    lr = ScraperReceiver()
    lr.launch()
