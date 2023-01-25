import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/"
ANNIVERSARY_URL = "getAnniversaryInfo"
NATIONAL_HOLIDAY_URL = "getHoliDeInfo"
EXCLUDED_SEASON_URL = "getSundryDayInfo"
SEASON_URL = "get24DivisionsInfo"

SERVICE_KEY = "{{ INPUT YOUR SECRET KEY }}"
NUM_OF_ROWS = "100"


def parseDateKind(dateKind):
    if dateKind == "01":
        return "NATIONAL_HOLIDAY"
    elif dateKind == "02":
        return "ANNIVERSARY"
    elif dateKind == "03":
        return "SEASON"
    elif dateKind == "04":
        return "EXCLUDED_SEASON"
    else:
        return ""


def getHolidayData(url, solYear, f):
    # GET Data
    FULL_URL = BASE_URL + url + "?solYear=%s&serviceKey=%s&numOfRows=%s" % (solYear, SERVICE_KEY, NUM_OF_ROWS)
    if SEASON_URL == url:
        kst = "0120"
        sunLongitude = "285"
        FULL_URL += "&kst=%s&sunLongitude=%s" % (kst, sunLongitude)
    response = requests.get(FULL_URL)

    # XML Parsing
    soup = BeautifulSoup(response.text, 'lxml-xml')
    items = soup.find_all("item")

    # Create SQL File
    f.write("-- %s 총 %d개\n" % (url, len(items)))
    f.write(
        "INSERT INTO `holiday` (`holiday_type`, `date_name`, `holiday`, `date`, `created_date_time`, `updated_date_time`)\n\tVALUES\n")

    item_str = []
    for item in items:
        dateKind = parseDateKind(item.find("dateKind").get_text())
        dateName = item.find("dateName").get_text()
        isHoliday = 1 if item.find("isHoliday").get_text() == "Y" else 0
        locdate = datetime.strptime(item.find("locdate").get_text(), '%Y%m%d').strftime("%Y-%m-%d")
        # seq = item.find("seq").get_text()
        item_str.append("\t\t('%s', '%s', %s, '%s', now(), now())\n" % (dateKind, dateName, isHoliday, locdate))
    f.write(", ".join(item_str))
    f.write(";\n\n")


def holiday_crawler(solYear):
    f = open('holiday_info' + '_' + solYear + '.sql', 'w')
    getHolidayData(ANNIVERSARY_URL, solYear, f)
    getHolidayData(NATIONAL_HOLIDAY_URL, solYear, f)
    getHolidayData(EXCLUDED_SEASON_URL, solYear, f)
    getHolidayData(SEASON_URL, solYear, f)
    f.close()


holiday_crawler("2023")
