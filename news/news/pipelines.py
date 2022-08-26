# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import pymongo
from datetime import datetime
from scrapy.exceptions import CloseSpider

class PerSectionCsvPipeline:
    def open_spider(self, spider):
        self.file = open(f'{spider.configuration["name"]}_{spider.section["key"]}_{datetime.today().strftime("%Y-%m-%d")}.csv', 'w', newline='', encoding='utf-8')
        fieldnames = ['url', 'title', 'body', 'date', 'section']
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item

class MongoPipeline:

    duplicate_counter = 0
    duplicate_limit = 20

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['efimerida'] = spider.configuration["name"]
        duplicateKey = spider.configuration["duplicateKey"]
        
        doc = self.collection.find_one({duplicateKey: item[duplicateKey]})
        if doc:
            self.duplicate_counter+=1
            if self.duplicate_counter > self.duplicate_limit:
                spider.crawler.engine.close_spider(self, reason='duplicate limit reached')
        else:
            self.collection.insert_one(item)

        return item

class NewsPipeline:
    def process_item(self, item, spider):
        return item
