import json
import sys
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from spiders.sigmalive import PageSpider
from spiders.brief import BriefSpider

args = sys.argv

spider_map = {
    "page": PageSpider,
    "brief": BriefSpider
}

def read_configuration_file(filename):
    with open(f'configurations/{filename}.json', 'r', encoding='utf-8') as jsonfile:
        return json.load(jsonfile)

configuration = read_configuration_file(args[1])
configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    for section in configuration['sections']:
        yield runner.crawl(spider_map[configuration['spider']], section=section, configuration=configuration)
    
    reactor.stop()

crawl()
reactor.run() 