import abc

import requests
from bs4 import BeautifulSoup

from webextractors.tools.proxies_manager import ProxyManager
from webextractors.tools.user_agent_management import UserAgentManager


# class Extractor(Logger):
class Extractor:
    def __init__(self, proxy=None):
        self.ua_manager = UserAgentManager()
        self.have_proxy = proxy
        if self.have_proxy:
            self.proxies_manager = ProxyManager()

    def _get_url(self, url, retry=3):
        if retry < 1:
            return None
        headers = {
            "User-agent": self.ua_manager.get_random_user_agent()
        }
        if self.have_proxy:
            proxies = self.proxies_manager.get_random_proxy()
            print(proxies)

            try:
                response = requests.get(url, headers=headers, proxies=proxies)
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print('Forbidden...')
                    self.proxies_manager = ProxyManager()
                    self._get_url(url, retry=retry - 1)
            except Exception as e:
                print(e.__traceback__)
                print(type(e))
                print("Reloading proxies...")
                self.proxies_manager = ProxyManager()
                self._get_url(url, retry=retry - 1)
        else:
            return requests.get(url, headers=headers, timeout=3)


    @abc.abstractmethod
    def extract_url(self, url, params):
        return

    def get_soup(self, url):
        try:
            response = self._get_url(url)
        except Exception as e:
            print(e)
            response = self._get_url(url)

        if not response: return None
        if response.status_code == 200: return BeautifulSoup(response.text, 'lxml')
        return None


if __name__ == "__main__":
    extractor = Extractor("TEST")
    url = "https://www.meilleursagents.com/"
    print(extractor.get_soup(url).find("h1").text)
