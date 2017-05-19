import re
from urllib.parse import urlparse

import ftfy


def remove_back_slash(x):
    return remove_double_blank(x.translate(str.maketrans("\n\t\r", "   "))).strip()


def remove_double_blank(x):
    return x.replace("  ", " ")


def extract_domain(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc, parsed_uri.hostname


def clean_html_string(x):
    return ftfy.fix_encoding(ftfy.fix_text(x.replace("\n", "").replace("\t", "").strip(), normalization='NFKC'))


def get_price(x):
    return int(get_number_from_string(x.replace("€", "")))


def get_date(x):
    regex = re.compile("[0-9]{2}/[0-9]{2}/[0-9]{4}")
    return re.findall(regex, x)


def get_code_post(x):
    regex = re.compile("[0-9]{5}")
    return re.findall(regex, x)


def get_number_from_string(x):
    try:
        return float(re.search("(\d+[\s\,]*\d+[\s\,]*\d*)", x).group(1).replace(" ", "").replace(",", "."))
    except Exception as e:
        return x
