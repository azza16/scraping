import scrapy
from datetime import datetime
from dateutil import parser
import re
import time

from selenium.webdriver.common.action_chains import ActionChains

from scrapy_selenium import SeleniumRequest

class BriefSpider(scrapy.Spider):
    name = "brief"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    page_counter = 1

    def __init__(self, *args, **kwargs):
        super(BriefSpider, self).__init__(*args, **kwargs)
        self.start_url = f'{self.configuration["startUrl"]}{self.section["value"]}'

    def start_requests(self):
        yield SeleniumRequest(url=self.start_url, callback=self.parse)

    def parse(self, response):
        driver = response.request.meta['driver']
        while True:
            for link in driver.find_elements_by_css_selector(self.configuration['articleLinkSelector']):
                link = link.get_attribute('href')
                if "linkFilter" in self.section and self.section["linkFilter"]:
                    match = re.search(self.section["linkFilter"], link)
                    if not match:
                        continue

                if "isLinkSelectorRelative" in self.configuration and self.configuration["isLinkSelectorRelative"]:
                    link = f'{self.configuration["startUrl"]}{link}'

                if "removeW" in self.configuration and self.configuration["removeW"]:
                    link = link.replace("www.", "")
                    
                yield scrapy.Request(link, self.parse_article)

            if self.page_counter < self.configuration['numberOfPages']:
                buttons = driver.find_elements_by_css_selector(self.configuration['loadMoreSelector'])
                for button in buttons:
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(5)
                        self.page_counter+=1
                        break
                    except:
                        pass
            else:
                break


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