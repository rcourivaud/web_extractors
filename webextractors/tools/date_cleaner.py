import datetime
import time

date_mapper = {"janvier": "01",
               "février": "02",
               "mars": "04",
               "avril": "04",
               "mai": "05",
               "juin": "06",
               "juillet": "07",
               "août": "08",
               "septembre": "09",
               "octobre": "10",
               "novembre": "11",
               "décembre": "12"}


def turn_date_leboncoin_in_unix(date_string):
    splits = date_string.split()
    num = splits[0]
    month = splits[1]
    hour = splits[3]
    year = str(datetime.datetime.today().year)

    date_clean = "{0}/{1}/{2}-{3}".format(num, date_mapper[month], year, hour)
    return int(time.mktime(datetime.datetime.strptime(date_clean, "%d/%m/%Y-%H:%M").timetuple()))


def turn_date_logicimmo_in_unix(date_string):
    return int(time.mktime(datetime.datetime.strptime(date_string, "%d/%m/%Y").timetuple()))
