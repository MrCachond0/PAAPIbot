import os
import json

POSTED_TWEETS_FILE = 'posted_tweets.json'

def load_posted_tweets():
    if os.path.exists(POSTED_TWEETS_FILE):
        with open(POSTED_TWEETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            # Estructura nueva
            all_tweets = set(data.get('promocionales', []) + data.get('valiosos', []))
        else:
            # Estructura antigua (lista)
            all_tweets = set(data)
        return all_tweets
    return set()

def register_tweet(tweet_text):
    # Solo guarda el texto, para scripts de prueba
    if os.path.exists(POSTED_TWEETS_FILE):
        with open(POSTED_TWEETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            if 'pruebas' not in data:
                data['pruebas'] = []
            data['pruebas'].append(tweet_text)
        else:
            data.append(tweet_text)
    else:
        data = {'pruebas': [tweet_text]}
    with open(POSTED_TWEETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def is_duplicate(tweet_text):
    all_tweets = load_posted_tweets()
    return tweet_text in all_tweets
