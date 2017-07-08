from gmc_extractors.lc_scraper import LCScraper
from web_extractors.archi.worker import Worker

if __name__ == "__main__":
    lcs = LCScraper()
    scrapers = {
        "la_centrale": lcs
    }
    scraper = Worker("ironman.bondevisite.fr", 5672, "admin", "Ijgige1976", all_scrapers=scrapers)
    scraper.launch()
