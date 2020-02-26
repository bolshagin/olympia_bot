import requests

from lxml import html
from constants import URL_VISIT


def get_visitors(url=URL_VISIT):
    page = requests.get(url, verify=False)
    tree = html.fromstring(page.content)
    pool_visitors = tree.xpath('//span[@class="zn"]/text()')
    if pool_visitors[0] == '-':
        return None
    pool_visitors = list(map(int, pool_visitors))
    return pool_visitors
