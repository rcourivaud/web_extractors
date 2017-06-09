import urllib

import html2text
from bs4 import BeautifulSoup
import re

from tqdm import tqdm
from webextractors.tools.htmlcleaner import clean_html_string

from web_extractors.archi.extractor import Extractor
from web_extractors.tools.htmlcleaner import extract_domain, remove_back_slash
from web_extractors.meta_extractors import ContactExtractor, SocialExtractor


class Crawler(Extractor):
    def __init__(self):
        super().__init__()

        self.bad_extensions = {"pdf", "xls", "doc", "ppt", "rtf",
                               "odt", "zip", "tar.gz", "tar",
                               "exe", "jpg", "png", "jpeg", "bmp",
                               "gif", "mp3", "flv", "rar", "ogv",
                               "avi", "mp4", "mkg", "ps", "ogg",
                               "webm", "ogm", "pps", "pptx", "docx",
                               "xlsx", "mpg", "mov", "mkv", "mpeg",
                               "m4v", "iso"}

        self.scores = {

        }


        self.contact_extractor = ContactExtractor()
        self.social_extractor = SocialExtractor()

    def get_text_from_page(self, url):
        if not self.is_valid_url(url):
            return ""

        page_source = self.get_soup(url)
        texts = page_source.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False
            if len(element) < 3:
                return False
            return True

        visible_texts = " ".join(list(filter(visible, texts)))
        return str(html2text.html2text(visible_texts))#, str(page_source)

    def is_valid_url(self, url):
        return bool(urllib.parse.urlparse(url).scheme)

    def crawl_website(self, website):
        response = self._get_url(website.base_url)
        page_source = response.text
        if "https:" in website.base_url:
            http = "https"
        else:
            http = "http"

        website.content = response.content
        website.headers = response.headers

        # Extract Domain
        website.domain = extract_domain(website.base_url)[0]

        # remove scripts and head text
        soup = BeautifulSoup(page_source, "lxml")
        [s.extract() for s in soup.findAll('script')]
        soup.find("head").extract()

        website.links.update([elt["url"] for elt in self._get_all_links(str(soup), website.domain, http)])
        for link in tqdm(website.links):
            t = self.get_text_from_page(link)
            website.text += " " + t
        return website

    def score_links(self, links):
        pass

    def _get_all_links(self, page, domain_url, http):
        soup = BeautifulSoup(page, 'lxml')
        all_links = [self.create_item(elt, domain_url, http) for elt in soup.findAll("a")]
        return [url for url in all_links if self._is_valid_url(url, domain_url=domain_url)]

    def _is_valid_url(self, url, domain_url):
        if not url["title"] or url["title"] == "" or not url['url']:
            return False

        key = url['url'].split("#")[0]
        if len(key) < 1:
            return False
        elif domain_url not in url['url']:
            return False
        if not all([self.bad_extensions not in list(url)]):
            return False
        return True

    def create_item(self, element_web, base_domain, http):
        title = remove_back_slash(element_web.text)
        if not element_web.get("href"):
            url = None
        else:
            if "http" in element_web["href"]:
                url = element_web["href"]
            elif "//" in element_web["href"]:
                url = http + element_web["href"]
            elif element_web["href"].count('/') and element_web["href"].endswith("/"):
                url = http + "://" + base_domain + "/" + element_web["href"]
            elif '/' not in element_web["href"]:
                url = http + "://" + base_domain + "/" + element_web["href"]
            else:
                url = http + "://" + base_domain + element_web["href"]

        return dict(url=url, title=title)

    def extract_meta_data(self, website):
        website.data["meta"] = self.contact_extractor.extract(text=website.text,
                                                              domain=website.domain, )
        website.data["meta"]["social"] = self.social_extractor.extract_social_media_from_response(content=website.content,
                                                                                                  header=website.headers)
        return website

    def extract_title_description(self, website):
        soup = BeautifulSoup(website.content)
        result = {}
        title = soup.find("title")
        description = soup.find("description")
        if title: result["title"] = clean_html_string(title.text)
        if description: result["description"]= clean_html_string(title.text)

        website.data.update(result)
        return website




    """
    To implement,
        return json with crawl result
    """
    def extract(self, message):
        website = Website(message["url"])
        website = c.crawl_website(website)
        website = c.extract_meta_data(website)
        website = c.extract_title_description(website)

        return website.get_data()


class Website:
    def __init__(self, url):
        self.base_url = url
        self.links = set()
        self.text = ''
        self.data = {}
        self.domain = ''


    def get_data(self):
        return {
            "data":self.data,
            "text":self.text,
            "links":self.links
        }



if __name__ == "__main__":
    c = Crawler()
    # website = Website("https://bondevisite.fr/")
    # website = Website("https://bondevisite.fr/")
    website = Website("http://www.adiosparis.fr/")
    # website = Website("http://simonvidal.fr/")
    # website = Website("https://fr.wikipedia.org/wiki/Annuaire")

    print(website.data)
