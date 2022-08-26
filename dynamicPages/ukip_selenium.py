import time
import csv
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

class SeleiumCrawler:
    def __init__(self) -> None:
        self.driver = self.initialize_driver()
        self.main()

    @staticmethod
    def initialize_driver():
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        return webdriver.Chrome("chromedriver", options=chrome_options)

    def main(self):
        counter = 0
        max_items = 10

        with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'body']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            self.driver.get("https://www.ukip.org/the-party-of-law-and-order")
            time.sleep(2)

            while counter < max_items:
                print(counter)
                print(self.driver.current_url)
                try:
                    title = self.driver.find_element_by_css_selector('.u_1668470589 h3').text
                    body = self.driver.find_element_by_css_selector('.u_1250789679').text
                    writer.writerow({
                        'url': self.driver.current_url,
                        'title': title,
                        'body': body
                    })
                    counter +=1
                except:
                    pass

                try:
                    next_href = self.driver.find_element_by_css_selector('.dmBlockElement a:last-of-type').get_attribute('href')
                    self.driver.get(next_href)
                    time.sleep(2)
                except:
                    break

            self.driver.quit()
            

SeleiumCrawler()

