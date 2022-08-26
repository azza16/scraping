# -*- coding: utf-8 -*-
import googleapiclient.discovery
import json

configuration = {
            "part":"snippet",
            "videoId":"Ro0Q4ehyGQc",
            "textFormat":"plainText",
            "maxResults":100,
            "searchTerms": "smart"
        }

class YouTubeCrawler():
    def __init__(self, configuration) -> None:
        self.configuration = configuration
        self.api = self.initialize_api()
        self.main()

    @staticmethod
    def initialize_api():
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = ""

        return googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = DEVELOPER_KEY)

    def main(self):
        request = self.api.commentThreads().list(**self.configuration)

        response = request.execute()

        with open('results.json', encoding='utf-8', mode='w') as outfile:
            json.dump(response, outfile, ensure_ascii=False, indent=4)


YouTubeCrawler(configuration)