import html2text
from bs4 import BeautifulSoup

from web_extractors.archi.extractor import Extractor
from web_extractors.tools.htmlcleaner import extract_domain, remove_back_slash


class Crawler(Extractor):
    def __init__(self):
        super().__init__("Crawler")
        pass

    def get_text_from_page(self, url):
        page_source = self._get_url(url).text
        return html2text.html2text(page_source)

    def crawl_website(self, url):
        self.logger.debug("Crawl :  {}".format(url))
        page_source = self._get_url(url).text
        if "https:" in url:
            http = "https"
        else:
            http = "http"

        links_depth1 =  self._get_all_links(page_source, url, http)
        source_text = html2text.html2text(page_source)
        for link in links_depth1:
            text = self.get_text_from_page(link["href"])

            source_text = source_text + " " + text

        return source_text

    def _get_all_links(self, page, base_url, http):
        soup = BeautifulSoup(page, 'lxml')
        domain_url = extract_domain(base_url)[0]

        all_links = [self.create_item(elt, domain_url, http) for elt in soup.findAll("a")]
        return [url for url in all_links if self._is_valid_url(url, domain_url=domain_url)]

    def _is_valid_url(self, url, domain_url):
        print(url)
        if url["title"] == "":
            return False
        elif '#' in url['url']:
            return False
        elif domain_url not in url['url']:
            return False
        elif "pdf" in url["url"]:
            return False
        elif "png" in url["url"].lower():
            return False
        elif "jpg" in url["url"].lower():
            return False
        else:
            return True

    def create_item(self, element_web, base_domain, http):
        title = remove_back_slash(element_web.text)
        if "http" in element_web["href"]:
            url = element_web["href"]
        elif "//" in element_web["href"]:
            url = http + element_web["href"]
        elif '/' not in element_web["href"]:
            url = http + "://" + base_domain + "/" + element_web["href"]
        else:
            url = http + "://" + base_domain + element_web["href"]

        return dict(url=url, title=title)

    """
    To implement,
        return json with crawl result
    """

    def extract(self, message):
        return ""
