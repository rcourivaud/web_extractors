import json

import requests
from bs4 import BeautifulSoup

from webextractors.archi.publisher import Publisher
from webextractors.tools.user_agent_management import UserAgentManager


class LeboncoinPublisher(Publisher):
    def __init__(self):
        super(LeboncoinPublisher, self).__init__("scraper")
        pass

    @staticmethod
    def create_all_links(n_page, type_of_offers):
        dict_urls_base = {
            "pros": "https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/occasions/?o={0}&f=c",
            "particuliers": "https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/occasions/?o={0}&f=p",
            "all": "https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/occasions/?o={0}"
        }
        return [dict_urls_base[type_of_offers].format(i) for i in range(1, n_page)]

    def start_to_scrap(self, n_page, type_of_offers="particuliers"):
        all_links = self.create_all_links(n_page=n_page, type_of_offers=type_of_offers)
        for link in all_links:
            print(link)
            print("Sending link to scrap " + link)
            message_to_send = json.dumps({"url": link, "params": None, "which": "leboncoin"})
            self.send_request(message=message_to_send)
        self.connection.close()


class MeilleurAgentPublisher(Publisher):
    def __init__(self):
        super().__init__("scraper")
        pass

    def start_to_scrap(self):
        with open("./all_cities_MA.json", 'r') as f:
            all_links = json.load(f)

        for city in all_links:
            postal_code = list(city.keys())[0]
            all_links = list(city.values())
            for link in all_links[0]:
                print("Sending link to scrap " + link)
                message_to_send = json.dumps(
                    {"url": link, "params": {"code_post": postal_code}, "which": "meilleursagents"})
                self.send_request(message=message_to_send)
        self.connection.close()

    def check_if_rows(self, base_link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(base_link, headers=headers)
        soup = BeautifulSoup(response.content, "lxml")
        list_link = soup.find(class_="list-link")
        try:
            first_link = list_link.find("li")
        except:
            print(base_link)
            return False
        if first_link.a:
            return True
        else:
            return False

    def get_rues_links(self, rues_links, base_link):
        if self.check_if_rows(base_link):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(rues_links, headers=headers)
            soup = BeautifulSoup(response.content, "lxml")
            url_ma = 'http://www.meilleursagents.com'
            rues = soup.findAll(class_="list-link")
            rues_links = []
            return [url_ma + rue.a["href"] for letter in rues for rue in letter.findAll("li") if
                    url_ma + rue.a["href"] != base_link]
        else:
            return []

    def get_all_cities(self):
        all_cities = []

        # urls of all cities
        for r, row in tqdm(df_villes.iterrows()):
            url = row.url
            rues_url = row.urls_rues
            all_links = self.get_rues_links(rues_links=rues_url, base_link=url)
            if len(all_links) > 0:
                all_cities.append({row.postal_code: all_links})


class LogicImmoPublisher(Publisher):
    def __init__(self):
        super(LogicImmoPublisher, self).__init__("scraper")
        self.name = "logicimmo"
        self.ua_manager = UserAgentManager()

    def get_number_of_pages(self, url):
        response = requests.get(url + "1", headers={"User-agent": self.ua_manager.get_random_user_agent()}).text
        soup = BeautifulSoup(response, 'lxml')
        try:
            return int(soup.find(class_="numbers").findAll("span")[-1].text)
        except:
            return 0

    def create_all_links(self):
        all_links = []
        url_departements = self.create_all_annonces_url()
        for url_dep in url_departements:
            print(url_dep)
            n_pages = self.get_number_of_pages(url_dep)
            for i in range(1, n_pages + 1):
                all_links.append(url_dep + str(i))

        return all_links

    def create_all_annonces_url(self):
        url_base = "http://www.logic-immo.com/vente-immobilier/options/grouplocalities={}/groupprptypesids=1,2,6,7,12,15/page="
        all_grouplocalities = ["{}_1".format(str(i)) for i in range(23, 121)]
        return [url_base.format(localities) for localities in all_grouplocalities]

    def start_to_scrap(self):
        all_links = self.create_all_links()
        for link in all_links:
            print(link)
            print("Sending link to scrap " + link)
            message_to_send = json.dumps({"url": link, "params": None, "which": "logicimmo"})
            self.send_request(message=message_to_send)
        self.connection.close()


if __name__ == '__main__':
    debug = False
    if debug:
        with open("./all_cities_MA.json", 'r') as f:
            all_links = json.load(f)
            print(len(all_links))
            print(sum([len(elt[list(elt.keys())[0]]) for elt in all_links]))
    else:
        # lp = MeilleurAgentPublisher()
        # lp.start_to_scrap()

        lp = LeboncoinPublisher()
        lp.start_to_scrap(29464, "pros")
        # lp.start_to_scrap(3, "pros")

        # lp = LogicImmoPublisher()
        # lp.start_to_scrap()
