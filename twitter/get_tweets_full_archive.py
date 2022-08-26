import requests
import time
import csv

bearer_token = ""

full_archive_endpoint = "https://api.twitter.com/2/tweets/search/all"

covid_params = {
    'query': 'covid (vaccine OR vaccination) lang:en',
    'tweet.fields': 'author_id,created_at,lang,source,conversation_id,in_reply_to_user_id,public_metrics,referenced_tweets,entities,attachments',
    'expansions': 'author_id,geo.place_id,referenced_tweets.id,attachments.media_keys',
    'user.fields': 'name,username,description,location,public_metrics',
    'media.fields': 'duration_ms,height,preview_image_url,public_metrics,width,alt_text',
    'place.fields': 'id,geo,country,country_code',
    'max_results': 100,
}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    counter = 0
    with open('results.csv', encoding='utf-8', mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        while True:
            results = connect_to_endpoint(full_archive_endpoint, covid_params)

            # check if any tweets were returned
            if 'data' not in results:
                break
            
            # for each tweet, extract and store all information requested
            for result in results['data']:
                try:
                    tweet = {
                        'created_at': result['created_at'],
                        'author_id': f"author_id_{result['author_id']}",
                        'text': result['text'],
                        'source': result['source'],
                        'lang': result['lang'],
                        'id': f"id_{result['id']}",
                        'retweet_count': result['public_metrics']['retweet_count'],
                        'reply_count': result['public_metrics']['reply_count'],
                        'like_count': result['public_metrics']['like_count'],
                        'quote_count': result['public_metrics']['quote_count'],
                    }

                    if 'conversation_id' in result:
                        tweet['conversation_id'] = f"conversation_id_{result['conversation_id']}"

                    if 'in_reply_to_user_id' in result:
                        tweet['in_reply_to_user_id'] = f"in_reply_to_user_id_{result['in_reply_to_user_id']}"
                                
                    if 'referenced_tweets' in result:
                        tweet['type'] = result['referenced_tweets'][0]['type']  
                        tweet['referenced_tweet_id'] = f"referenced_tweet_id_{result['referenced_tweets'][0]['id']}"

                    if 'attachments' in result:
                        if 'media_keys' in result['attachments']:
                            if 'media' in results['includes']:
                                media = next((x for x in results['includes']['media'] if x['media_key'] == result['attachments']['media_keys'][0]), None)
                                if media:
                                    tweet['media_type'] = media.get('type')
                                    tweet['media_height'] = media.get('height')
                                    tweet['media_duration_ms'] = media.get('duration_ms')
                                    tweet['media_preview_image_url'] = media.get('preview_image_url')
                                    tweet['media_width'] = media.get('width')
                                    tweet['media_alt_text'] = media.get('alt_text')
                                    if 'public_metrics' in media:
                                        tweet['media_view_count'] = media['public_metrics']['view_count']


                    if 'entities' in result:
                        if 'hashtags' in result['entities']:
                            tweet['entity_hashtags'] = ','.join(x['tag'] for x in result['entities']['hashtags'])
                        if 'mentions' in result['entities']:
                            tweet['entity_mentions'] = ','.join(x['username'] for x in result['entities']['mentions'])

                    if 'users' in results['includes']:
                        user = next((x for x in results['includes']['users'] if x['id'] == result['author_id']), None)
                        if user:
                            tweet['name'] = user['name']
                            tweet['description'] = user['description']
                            tweet['username'] = user['username']
                            tweet['location'] = user.get('location')
                            tweet['followers_count'] = user['public_metrics']['followers_count']
                            tweet['following_count'] = user['public_metrics']['following_count']
                            tweet['tweet_count'] = user['public_metrics']['tweet_count']
                            tweet['listed_count'] = user['public_metrics']['listed_count']

                    if 'geo' in result:
                        if 'places' in results['includes']:
                            place = next((x for x in results['includes']['places'] if x['id'] == result['geo']['place_id']), None)
                            if place:
                                tweet['place_id'] = place['id']
                                tweet['geo_full_name'] = place['full_name']
                                tweet['country_code'] = place['country_code']
                                tweet['country'] = place['country']
                                tweet['geo_coordinates'] = ','.join(str(c) for c in place['geo']['bbox'])

                    # write tweet to csv file
                    writer.writerow(tweet)
                except:
                    print("tweet error")
                    pass

            # handles pagination
            if 'next_token' in results['meta']:
                covid_params['next_token'] = results['meta']['next_token']
            else:
                break
            
            # wait betweent requests for 2 seconds
            counter+=1
            print(f"Fetched {str(counter * 100)} tweets so far")
            time.sleep(2)

if __name__ == "__main__":
    main()