import json
from eventregistry import *

API_KEY = 'your_api_key'

class EventRegistryCrawler():
    def __init__(self, keywords) -> None:
        self.api = self.initiliaze_api_and_params()
        self.params = self.initialize_params(keywords)

    def initiliaze_api(self):
        er = EventRegistry(apiKey = API_KEY)

    def initialize_params(self, keywords):
        q = QueryArticlesIter(
            keywords = QueryItems.OR(keywords.split(",")),
            isDuplicateFilter="skipDuplicates",
            lang="en",
            dataType = ["news", "blog"])
        )

        returnInfo = ReturnInfo(
            articleInfo=ArticleInfoFlags(socialScore=True),
            sourceInfo=SourceInfoFlags(title = True, description = True)
        )

        return {"q": q, "returnInfo": returnInfo}

    def execute_query(self):
        articles = []
        for article in self.params['q'].execQuery(self.api, sortBy = "date", maxItems = -1, returnInfo=self.params['returnInfo']):
            articles.append(article)
        
        return articles

    def main(self):
        results = self.execute_query()
        with open('results.json', 'w') as outfile:
            json.dump(results, outfile)

EventRegistryCrawler("trump,biden")