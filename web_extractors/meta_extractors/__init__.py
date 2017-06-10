import re
from urllib.parse import urlparse, urljoin, parse_qs

from html_to_etree import parse_html_bytes
from lxml import etree
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import FrenchStemmer
import nltk
from web_extractors.tools.social_extract import find_links_tree


class ContactExtractor:
    def __init__(self):
        self.regex_websites = re.compile(
            "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
        self.regex_email = re.compile("[a-z0-9\.\-_]+@[a-z0-9\.\-\_]+\.[a-z]{2,5}")
        self.regex_phones = re.compile(
            "0[1-9]{1}[\.\- ]{0,1}[0-9]{2}[\.\- ]{0,1}[0-9]{2}[\.\- ]{0,1}[0-9]{2}[\.\- ]{0,1}[0-9]{2}")

    def extract(self, text, domain):
        return {
            # "links": self.get_all_links(text, domain),
            "mails": list(set(self.get_all_emails(text))),
            "phones": list(set(self.get_all_phones(text)))
        }

    def get_all_links(self, x, domain):
        domain_clean = domain.replace(".fr", "").replace(".org", "").replace(".com", "")
        l = [elt for elt in re.findall(self.regex_websites, x) if domain not in elt]
        return l

    def get_all_emails(self, x):
        return re.findall(self.regex_email, x)

    def get_all_phones(self, x):
        return [self.clean_phone(elt) for elt in re.findall(self.regex_phones, x)]

    def clean_phone(self, x):
        return x.replace(".", "").replace("-", "")


class SocialExtractor:
    """
    Extracts social information on websites :
      Company Profile (url) for : twitter, facebook, linkedin, viadeo, googleplus
      Presence of videos (boolean) for : youtube, dailymotion, vimeo
    """

    def __init__(self):
        # Social: Facebook, Twitter, Google Plus, Linkedin, Viadeo, Instagram, YouTube, dailymotion, vimeo
        self.metas = ["twitter", "facebook", "linkedin",
                      "viadeo", "googleplus", "instagram",
                      "youtube", "dailymotion", "vimeo"]

    def extract_social_media_from_response(self, content, header):
        tree = parse_html_bytes(content, header.get('content-type'))
        print("Extract social media")
        result = {}

        for m in self.metas:
            for link in list(set(find_links_tree(tree))):
                if m in link:
                    result[m] = link
        return result


    def extract_social_media_links(self, x):
        html = etree.HTML(str(x))
        all_social_links = set(find_links_tree(html))
        result = {}
        for m in self.metas:
            for link in list(all_social_links):
                if m in link:
                    result[m] = link
        return result

    def extract(self, text):
        results = {}

        for m in self.metas:
            res = self._extract_social_link(link=text, meta=m)
            if res:
                results[m] = res

        return results

    def _extract_social_link(self, link, meta):
        """
        Switch toward specialized link extractors
        """
        if meta == "twitter":
            return self.extract_twitter(href=link)
        if meta == "facebook":
            return self.extract_facebook(href=link)
        if meta == "linkedin":
            return self.extract_linkedin(href=link)
        if meta == "viadeo":
            return self.extract_viadeo(href=link)
        if meta == "googleplus":
            return self.extract_googleplus(href=link)
        if meta == "instagram":
            return self.extract_instagram(href=link)
        if meta == "youtube":
            return self.extract_youtube(href=link)
        if meta == "dailymotion":
            return self.extract_dailymotion(src=link)
        if meta == "vimeo":
            return self.extract_vimeo(src=link)

    def extract_instagram(self, href):
        """
        Tries to extract Instagram account URL
        """
        m = re.search("(https?://instagram.com/.+])", href)
        if m is not None:
            return m.group(1)

        return None

    def get_facebook_account(self, url):
        # First lowercase the url
        url = url.lower()

        # First we select the right http://... part
        m = re.search("https?://(?:.+?\.)?facebook.com(/[a-z0-9\-]+)", url)
        if not m:
            return None
        path = m.group(1)

        # Replace multiple / by only one
        path = re.sub("/+", "/", path)

        # Remove first / if there is still one
        # path = re.sub("^/*", "", path)

        # Ajax redirections
        m = re.search("#!?(/.*)", path)
        if m:
            path = m.group(1)

        # Remove #fragments
        path = re.sub("#.*$", "", path)

        # Remove ?query
        path = re.sub("\\?.*$", "", path)

        # remove & (wrong url end)
        path = re.sub("(&|;).*$", "", path)

        # remove final spaces
        path = path.strip()

        # Blacklist
        BLACKLIST = [
            # All utility pages from facebook
            "/recover", "recover/initiate", "/dialog/", "oauth?", ".php", "/hashtag/", "/share",
            # Medias often points to timeline of people, not companies
            "/photos", "/media/", "/video/", "/media_set", "/notes/",
            # Other things to blacklist
            "/edit/", "/public/", "app_", "/events/"
        ]
        for blacklisted in BLACKLIST:
            if blacklisted in path:
                return None

        m = re.match("^/pages/(?:.*/)*(\d+)/?$", path)
        if m:
            return m.group(1)

        m = re.match("^/people/(?:.*/)*(\d+)$", path)
        if m:
            return m.group(1)

        m = re.match("^/(groups/[^/]+)", path)
        if m:
            return m.group(1)

        m = re.match("^/([^/]+)", path)
        if m:
            account = m.group(1)
            if "http:" in account or "https:" in account:
                return None
            return account

        return None

    def extract_vimeo(self, src):
        """
        Tries to extract vimeo URL to a video or channel
        """
        # <iframe src="http://player.vimeo.com/video/56553983?title=0&byline=0&portrait=0"></iframe>
        # http://www.vimeo.com/adiosparis
        m = re.search("(https?://player.vimeo.com/.+)", src)
        if m is not None:
            return m.group(1)

        return None

    def extract_dailymotion(self, src):
        """
        Tries to extract dailymotion URL to a video or channel
        """
        # <iframe frameborder="0" width="270" height="152" src="http://www.dailymotion.com/embed/video/xq6zpm?logo=0&hideInfos=1"></iframe>
        m = re.search("(https?://www.dailymotion.com/.+)", src)
        if m is not None:
            return m.group(1)

        return None

    def extract_youtube(self, href):
        """
        Tries to extract youtube URL to a video or channel
        """
        # href="http://www.youtube.com/embed/JW7jK3UXHQo?autoplay=1&rel=0"
        m = re.search("(https?://www.youtube.com/.+)", href)
        if m is not None:
            return m.group(1)

        return None

    def extract_twitter(self, href):
        """
        Tries to extract twitter account as @account_name
        """
        BLACKLIST = ["share", "home", "intent", "account", "search", "signup"]
        BLACKLIST += ["privacy", "timeline", "twitterapi", "articles"]
        BLACKLIST += ["twitter", "statuses"]

        # <a href="http://www.twitter.com/datapublica" target="_blank"><img src="/static/img/twitter_16.png" alt="twitter_16" width="16" height="16"> Twitter</a>
        m = re.search("twitter.com/"  # root
                      # optional fail from webmaster
                      "(?:https?://www.twitter.com/)?"
                      "(?:#!/)?"  # optionnal hashbang escape
                      "@?"  # optionnal @ before account
                      "(\w+)"  # account (\w → [a-zA-Z0-9_])
                      "(?:$|[/#?\"'])"  # must be terminated by end of string, or /#?, or "' if this was some javascript
                      "", href)

        if m is not None:
            account = m.group(1)

            # We ignore share buttons
            for blacklisted in BLACKLIST:
                if account.startswith(blacklisted):
                    return None
            return "@" + account.lower()

        return None

    def extract_facebook(self, href):
        """
        Tries to extract facebook account URL
        """

        # like box matching
        # <iframe src="http://www.facebook.com/plugins/likebox.php?href=https%3A%2F%2Fwww.facebook.com%2Fcompapharma&amp;width=250&amp;height=100&amp;show_faces=false&amp;colorscheme=light&amp;stream=false&amp;show_border=false&amp;header=false" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:250px; height: 100px;" allowTransparency="true"></iframe>
        if "//www.facebook.com/plugins/likebox.php" in href:
            params = parse_qs(urlparse(href).query)
            if "href" in params:
                href = params["href"][0]

        # <a href="http://www.facebook.com/datapublica" target="_blank"><img src="/static/img/facebook_16.png" width="16" height="16"> Facebook</a>
        facebook = self.get_facebook_account(href)
        if facebook is not None:
            return "http://www.facebook.com/" + facebook

        return None

    def extract_viadeo(self, href):
        """
        Tries to extract viadeo account URL
        """
        # http://www.viadeo.com/fr/profile/sas.neoppidum
        # country code is not always indicated
        m = re.search("(https?://www.viadeo.com/\w*/?profile/.+)", href)
        if m is not None:
            return m.group(1).lower()

        return None

    def extract_linkedin(self, href):
        """
        Tries to extract linkedin account URL
        """
        href = href.lower()
        # http://www.linkedin.com/company/data-publica
        m = re.search("https?://(?:www\.)?linkedin.com/(company/[^/]+)", href)
        if m is None:
            return None

        account = m.group(1)
        account = re.sub("\?.*$", "", account)
        account = re.sub("#.*$", "", account)
        account = "http://www.linkedin.com/%s" % account

        return account

    def extract_googleplus(self, href):
        """
        Tries to extract google+ account URL
        """
        # href="https://plus.google.com/110323587230527980117?prsrc=3"
        # href="https://plus.google.com/u/0/101330197763441062911/posts"
        m = re.search('(//plus.google.com/[0-9a-z]+)', href)
        if m is not None and "share?" not in m.group(1):
            return "https:" + m.group(1).lower()

        return None

class HistExtractor:
    def __init__(self):

        self.stemmer = FrenchStemmer()
        self.analyzer = CountVectorizer().build_analyzer()

        self.bad_words = ["src", 'html', 'ifram',
                        'allowtransparency','analytic','class',
                         'com','hidden','lien', 'lightwidget','overflow',
                         'row','script', 'scrolling','src','widget',"tous","jour","blog",
                            'width','wrapp', "les", "googl", "propos", "list"]
        self.stopwords = nltk.corpus.stopwords.words('french') + self.bad_words

        def stemmed_words(doc):
            return (self.stemmer.stem(w) for w in self.analyzer(doc) if w not in self.stopwords)

        self.cv = CountVectorizer(analyzer=stemmed_words, stop_words=self.stopwords)
        #self.cv = CountVectorizer(stop_words=self.stopwords)


    def get_histogram_from_string(self, x):
        hist = self.cv.fit_transform([x])
        dict_result =  {k:v for k,v in zip(self.cv.get_feature_names(), hist.toarray()[0]) if k not in self.bad_words}
        return dict_result


