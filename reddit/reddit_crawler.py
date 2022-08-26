import os
import sys
import praw
import time
import pymongo

submission_search = {
    "endpoint": "search/submissions",
    "itemLimit": 5,
    "params": {
        "submission_ids": "lky95g"
    }
}

subreddit_search = {
    "endpoint": "search/subreddits",
    "itemLimit": 5,
    "params": {
        "subreddits": "learnpython",
        "filter": 'hot',
        "limit": 1
    }
}

class RedditCrawler():
    def __init__(self, configuration) -> None:
        self.configuration = configuration
        self.comment_counter = 0
        self.wait_between_requests = 2
        self.collection = self.initialize_mongo()
        self.api = self.initialize_reddit_instance()
        self.endpoint_map = {
            'search/subreddits': self.search_subreddits,
            'search/submissions': self.search_submissions
        }
        self.main()

    def initialize_mongo(self, db_name, collection_name):
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]
        return collection

    def initialize_reddit_instance(self):
        return praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent="Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            ratelimit_seconds=300,
        )

    def insert_document(self, comment):
        self.collection.insert_one(comment)

        self.comment_counter+=1

        if self.comment_counter >= self.configuration['itemLimit']:
            return True

        return False
    
    def get_submission_comments(self, submission):
        for comment in submission.comments.list():
            comment = {
                'id': comment.id,
                'body': comment.body,
                'score': comment.score,
                'created_utc': comment.created_utc,
                'author_name': comment.author.name,
                'author_karma': comment.author.comment_karma,
                'submission': comment.submission.title,
                'subreddit': comment.subreddit.name
            }
            
            r = self.insert_document(comment)
            if r:
                sys.exit()

        time.sleep(self.wait_between_requests)

    # accept a list of submission ids to get comments from
    def search_submissions(self, params):
        for sid in params['submission_ids'].split(','):
            submission = self.api.submission(id=sid)
            submission.comments.replace_more()
            self.get_submission_comments(submission)
    
    # sort subreddit based on configuration
    def get_subreddit_sort(self, subreddit, filter):
        sort_map = {
            'hot': subreddit.hot,
            'top': subreddit.top,
            'controversial': subreddit.controversial,
            'rising': subreddit.rising,
            'gilded': subreddit.gilded,
            'new': subreddit.new
        }

        return sort_map[filter]

    # accept 1: subreddit name, 2: sorting type (hot, controversial new etc), 3: number of submissions to get
    def search_subreddits(self, params):
        for s in params['subreddits'].split(','):
            subreddit = self.api.subreddit(s)
            subreddit_sorted = self.get_subreddit_sort(subreddit, params['filter']) 
            for submission in subreddit_sorted(limit=params['limit']):
                self.get_submission_comments(submission)

    def main(self):
        self.endpoint_map[self.configuration['endpoint']](self.configuration['params'])

RedditCrawler(subreddit_search)
