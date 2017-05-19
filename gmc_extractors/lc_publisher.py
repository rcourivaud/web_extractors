import json

import requests
import requests_cache
from bs4 import BeautifulSoup
from pandas_mysql import PandasMySQL
from tqdm import tqdm

from web_extractors.archi.publisher import Publisher


class LCPublisher(Publisher):
    def __init__(self, host, port, user, pwd):
        super().__init__(host, port, user, pwd)
        self.pms = PandasMySQL(host="a824b98c-10fa-48f0-bf2a-507af0ec7dd0.pdb.ovh.net",
                               port=21616, usr="admin", pwd="givemeacaresieeparis2017")
        self.df_models = self.pms.read_table("data_car", "models")
        requests_cache.install_cache("brands", expire_after=1000000000)

    def get_all_urls_from_page(self, url_base):
        req = requests.get(url_base)
        soup = BeautifulSoup(req.text, "lxml")
        try:
            n_pages = list(range(1, int(soup.find(class_="pagination").findAll("li")[-2].text)))
            url_tmp = url_base.replace(".html", "-{}.html")
            urls = [url_tmp.format(i) for i in n_pages]
        except Exception as e:

            urls = [url_base]
        return urls

    def get_all_offers_from_page(self, url_page):
        req = requests.get(url_page)
        soup = BeautifulSoup(req.text, "lxml")
        all_links = []
        for ad in soup.findAll(class_="adContainer "):
            link = "http://www.lacentrale.fr" + ad.findAll("a")[1]["href"]
            all_links.append(link)
        return all_links

    def start_to_scrap(self):
        # l_total = []
        for r, row in tqdm(self.df_models.iterrows()):
            all_pages_links = self.get_all_urls_from_page(row.lacentrale_link)
            all_links_model = []
            for page in all_pages_links:
                all_links_model.extend(self.get_all_offers_from_page(page))

            brand_dict = {
                "index": int(r),
                'brand_index': int(row.brand_index),
                "lacentrale_name": str(row.lacentrale_name)
            }
            for link in all_links_model:
                print("Sending link to scrap " + link)
                message_to_send = json.dumps({"url": link, "params": brand_dict, "which": "la_centrale"})
                self.send_request(message=message_to_send)

        #     l_total.append({
        #         "index": int(r),
        #         'brand_index': int(row.brand_index),
        #         "lacentrale_name": str(row.lacentrale_name),
        #         "all_links": all_links_model
        #     })
        #
        # return l_total
    #
    # def start_to_scrap(self):
    #     all_brands = self.get_all_brands_links()
    #     for brands in all_brands:
    #         for link in brands["all_links"]:
    #             print("Sending link to scrap " + link)
    #             message_to_send = json.dumps({"url": link, "params": brands, "which": "la_centrale"})
    #             self.send_request(message=message_to_send)
    #     self.connection.close()


if __name__ == "__main__":
    lcp = LCPublisher(host="ironman.bondevisite.fr", port=5672, user="admin", pwd="Ijgige1976")
    lcp.start_to_scrap()
