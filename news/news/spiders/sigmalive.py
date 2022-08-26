import scrapy
from datetime import datetime
from dateutil import parser
import re

class PageSpider(scrapy.Spider):
    name = "pagespider"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    page_counter = 1

    def __init__(self, *args, **kwargs):
        super(PageSpider, self).__init__(*args, **kwargs)
        self.page_value = self.configuration["nextPage"]["initialValue"]
        self.start_url = f'{self.configuration["startUrl"]}{self.section["value"]}{self.configuration["nextPage"]["suffix"]}'
        self.start_urls = [f'{self.start_url}{self.page_value}']

    def parse(self, response):
        for link in response.css(self.configuration['articleLinkSelector']):
            link = link.attrib['href']
            if "articleLinkFilter" in self.configuration and self.configuration["articleLinkFilter"]:
                match = re.search(self.configuration["articleLinkFilter"], link)
                if not match:
                    continue
 
            if "isLinkSelectorRelative" in self.configuration and self.configuration["isLinkSelectorRelative"]:
                link = f'{self.configuration["startUrl"]}{link}'

            if "removeW" in self.configuration and self.configuration["removeW"]:
                link = link.replace("www.", "")
                
            yield scrapy.Request(link, self.parse_article)

        if self.page_counter < self.configuration['numberOfPages']:
            self.page_value += self.configuration["nextPage"]["increment"]
            yield response.follow(f'{self.start_url}{self.page_value}', callback=self.parse)
            
            self.page_counter+=1

    def parse_article(self, response):
        article_info = {
            'url' : response.url,
            'section': self.section["key"]
        }

        for selector in self.configuration['selectors']:
            if selector['multiple']:
                article_info[selector['key']] = ' '.join([text.strip() for text in response.css(f'{selector["value"]}').getall()])
            else:
                article_info[selector['key']] = response.css(f'{selector["value"]}').get().strip()
                if "dateFormat" in selector and selector["dateFormat"]:
                    if selector["dateFormat"] == "parse":
                        article_info[selector['key']] = parser.parse(article_info[selector['key']])
                    else:
                        article_info[selector['key']] = datetime.strptime(article_info[selector['key']], selector["dateFormat"])

        yield article_info