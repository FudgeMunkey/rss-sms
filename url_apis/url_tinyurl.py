from url_apis.url_api import UrlApi
import requests


class UrlTinyurl(UrlApi):

    def shorten_url(self, url):
        TINY_URL_PREFIX = "http://tinyurl.com/api-create.php?url="

        short_url = requests.get(TINY_URL_PREFIX + url).text.split('//')[1]

        return short_url
