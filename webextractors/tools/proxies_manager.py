import itertools
import random
import re
import time

import requests
from bs4 import BeautifulSoup


class ProxyManager:
    def __init__(self, url='https://hidemy.name/en/proxy-list/'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.proxies = self.load_proxies(url)

    def get_random_proxy(self):
        try:
            return random.choice(self.proxies)
        except Exception as e:
            time.sleep(10)

    def load_proxies(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        data = []
        table = soup.find('table', attrs={'class': 'proxy__t'})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [elt.text.strip() for elt in cols]
            cols.append(int(re.search("([0-9]*) ", cols[3]).group(1)))
            data.append([elt for elt in cols if elt])

        list_name = ["ip", "port", "localisation", "ping", "types", "anonimity", "lastupdated", "ping_clean"]
        n_proxies_http = 0
        n_proxies_https = 0
        min_ping = 0

        while n_proxies_http < 5 and n_proxies_https < 5:
            min_ping += 100
            list_data_http = [{list_name[e]: elt for e, elt in enumerate(proxy) if e in [0, 1]} for proxy in data if
                              proxy[7] < min_ping and 'HTTP' in proxy[4]]
            list_data_https = [{list_name[e]: elt for e, elt in enumerate(proxy) if e in [0, 1]} for proxy in data if
                               proxy[7] < min_ping and 'HTTPS' in proxy[4]]
            n_proxies_http = len(list_data_http)
            n_proxies_https = len(list_data_https)

        l_product = list(itertools.product(list_data_http, list_data_https))
        l_final = [{"http": 'http://{}:{}'.format(elt[0]['ip'], elt[0]['port']),
                    "https": 'https://{}:{}'.format(elt[1]['ip'], elt[1]['port'])} for elt in l_product]
        print("{} proxies were found ".format(str(len(l_final))))
        return l_final


if __name__ == "__main__":
    pm = ProxyManager()
    print(pm.get_random_proxy())
