import re
import urllib

import html2text
from bs4 import BeautifulSoup
from ftfy import fix_text
from tqdm import tqdm

from web_extractors.archi.extractor import Extractor
from web_extractors.meta_extractors import ContactExtractor, SocialExtractor, HistExtractor
from web_extractors.tools.htmlcleaner import extract_domain, remove_back_slash, clean_html_string


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

        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.ignore_images = True
        self.h2t.ignore_emphasis = True

        self.contact_extractor = ContactExtractor()
        self.social_extractor = SocialExtractor()
        self.histgram_extractor = HistExtractor()

    def _get_text_from_page(self, url):
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

        return str(html2text.html2text(re.sub("\<iframe.+\>",
                                              " ",
                                              re.sub("\n",
                                                     " ", visible_texts)))).replace("\n", " ").lower() # , str(page_source)

    def get_text_from_page(self, page_source):

        return self.h2t.handle(page_source).replace("\n", " ").replace("\t", " ")

    def is_valid_url(self, url):
        return bool(urllib.parse.urlparse(url).scheme)

    def score_url(self, url):
        contact_about_l = ["contact", "propos", "about", "nous"]
        if any([a in b for a in contact_about_l for b in url.values()]):
            return 1
        else:
            return 2

    def get_sorted_links(self, website, soup, n=20):
        all_links = self._get_all_links(str(soup), website.domain, website.http)
        return [elt["url"] for elt in list(sorted(all_links, key=lambda x: self.score_url(x)))][0:20]

    def crawl_website(self, website):
        response = self._get_url(website.base_url, timeout=15)
        page_source = response.text

        website.content = response.content
        website.headers = response.headers

        website.text += " " + fix_text(self.get_text_from_page(page_source), normalization="NFKC")

        # Extract Domain

        # remove scripts and head text
        soup = BeautifulSoup(page_source, "lxml")
        [s.extract() for s in soup.findAll('script')]
        soup.find("head").extract()
        fixed_links = list(website.links)

        for link in tqdm(fixed_links):
            if link not in website.crawled_links:
                website.crawled_links.append(link)
                if self.is_valid_url(link):
                    try:
                        page_source = self._get_url(url=link, retry=2, timeout=8).text
                        soup = BeautifulSoup(page_source, "lxml")
                        t = self.get_text_from_page(page_source)
                        website.links.update(self.get_sorted_links(website=website, soup=soup))
                        website.out_links.update(self.get_outlinks(website=website, soup=soup))
                        website.text += " " + fix_text(t, normalization="NFKC")
                    except:pass
        return website

    def get_outlinks(self, website, soup):
        all_links = [urllib.parse.urlparse(elt.get("href")).netloc for elt in soup.findAll("a") if
                     elt.get("href") and website.domain not in elt.get("href")]
        return [elt for elt in all_links if elt]

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
            if element_web["href"].startswith("#"):
                url = None
            elif "http" in element_web["href"]:
                url = element_web["href"]
            elif "//" in element_web["href"]:
                url = http + element_web["href"]
            elif element_web["href"].count('/') and element_web["href"].endswith("/"):
                url = http + "://" + base_domain + "/" + element_web["href"]
            elif '/' not in element_web["href"]:
                url = http + "://" + base_domain + "/" + element_web["href"]
                if ".html" in element_web["href"] or ".php" in element_web["href"]:
                    title = element_web["href"].replace(".html", "").replace(".php", "")
            else:
                url = http + "://" + base_domain + element_web["href"]

        return dict(url=url, title=title)

    def extract_meta_data(self, website):
        website.data["meta"] = self.contact_extractor.extract(text=website.text,
                                                              domain=website.domain, )
        website.data["meta"]["social"] = self.social_extractor.extract_social_media_from_response(
            content=website.content,
            header=website.headers)
        website = self.extract_histogram(website=website)
        return website

    def extract_title_description(self, website):
        soup = BeautifulSoup(website.content, "lxml")
        result = {}
        title = soup.find("title")
        description = soup.find("description")
        if title: result["title"] = clean_html_string(title.text)
        if description: result["description"] = clean_html_string(title.text)

        website.data.update(result)
        return website

    def extract_histogram(self, website):
        website.data["histogram"] = self.histgram_extractor.get_histogram_from_string(website.text)
        website.data["twentywords"] = [k for k,v in sorted(website.data["histogram"].items(),
                                                           key=lambda x: x[1], reverse=True)][0:20]
        return website

    """
    To implement,
        return json with crawl result
    """
    def extract(self, message):
        website = Website(message["url"])
        depth = message.get("depth", 2)
        try:
            for i in range(depth):
                website = self.crawl_website(website)
            website = self.extract_meta_data(website)
            website = self.extract_title_description(website)

            return website.get_data()
        except:
            return None


class Website:
    def __init__(self, url):
        self.base_url = url
        self.links = set([url])
        self.text = ''
        self.data = {}
        self.domain = extract_domain(self.base_url)[0]
        self.http = "https" if "https" in url else "http"

        self.out_links = set()
        self.crawled_links = []

    def get_data(self):
        self.data.update({
            "text": fix_text(self.text, normalization="NFKC"),
            "links": list(self.links),
            "outlinks": list(self.out_links),
            "links": list(self.crawled_links),
            "_id": self.domain,
            "http": self.http
        })

        return self.data


if __name__ == "__main__":
    c = Crawler()
    # website = Website("https://bondevisite.fr/")
    # website = Website("https://bondevisite.fr/")
    website = Website("http://raphaelcourivaud.fr")
    # website = Website("http://simonvidal.fr/")
    # website = Website("https://fr.wikipedia.org/wiki/Annuaire")
    print(c.extract({"url":website.base_url}))
