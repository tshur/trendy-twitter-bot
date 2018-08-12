import markovify
import random
import requests
import tweepy
import time
import json
from contextlib import redirect_stdout
from collections import Counter
import re
import os
import sys
import nltk
import twint
import argparse
import datetime
import asyncio

# Load Twitter application credentials (API keys)
from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET, GIPHY_API_KEY
from utils import POSifiedNewlineText, EmojiTranslator, contains_one_of, get_gif, load_corpus

SAN_JOSE = (37.3382, -121.8863)
SAN_FRANCISCO = (37.7749, -122.4194)
UNITED_STATES_WOEID = 23424977

BOT_DESC_ITEMS = ['д', 'site', 'link', 'url', 'tweet', '.ly', 'http', '#FollowBack', '#followback']
FILTER_ITEMS = ['.gl', 'http']
QUERY_TERMS = ['', 'the', 'I', 'and', 'a', 'that', 'my']

class TwitterBot:
    def __init__(self):
        """Performs authentication and initializes a tweepy api object."""

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def tweet_message(self, message):
        """Tweets a message!"""

        self.api.update_status(status=message)
        time.sleep(20)

    def reciprocate(self):
        print('Reciprocating based on users that have interacted with the bot...')
        with open('checked.log', 'r') as fp:
            marked = set(fp.read().strip().split('\n'))

        unmarked = set()
        for page in tweepy.Cursor(self.api.followers_ids, screen_name='the_reaI_tim').pages():
            for userid in page:
                if str(userid) not in marked:
                    unmarked.add(userid)
                    user_json = self.api.get_user(userid)._json
                    if not_bot(user_json) and random.random() < 0.9:
                        try:
                            print('Following back user with id {}...'.format(userid))
                            self.follow(userid)
                            self.like_back(userid)
                        except:
                            print('Like-back/follow failed on user {}.'.format(userid))

                #time.sleep(60)

        # with open('tocheck.log', 'r') as fp:
        #     tocheck = set(fp.read().strip().split('\n'))
        #     userids = [self.api.get_user(uname)._json['id'] for uname in tocheck if uname]
        #     #time.sleep(20)

        # for userid in userids:
        #     if str(userid) not in marked and userid < 964792436420653056:
        #         self.like_back(userid)
        #         unmarked.add(userid)

        with open('tocheck.log', 'w') as fp:
            fp.write('')

        with open('checked.log', 'a') as fp:
            fp.write('\n')
            for userid in unmarked:
                fp.write(str(userid) + '\n')

    def follow(self, user_id):
        # print('Following user with id {}...'.format(user_id))
        try:
            self.api.create_friendship(user_id)
            time.sleep(20)
        except:
            print('Failed to follow user with id {}.'.format(user_id))

    def generate_corpus(self, query, limit=20000, detail=False, old=False, filter_fn=lambda x: True):
        print('Generating a corpus by scraping {} tweets...'.format(limit))
        date = datetime.date.today()
        day = datetime.timedelta(days=1)
        if old:
            until = datetime.datetime.strftime(date, '%Y-%m-%d')
        else:
            until = datetime.datetime.strftime(date, '%Y-%m-%d')
        since = datetime.datetime.strftime(date - 2*day, '%Y-%m-%d')

        args = ['-t', '1', '-l', 'en', '--since', str(since),
                '--until', str(until), '-s', str(query), '--limit', str(limit)]
        if not detail:
            args.append('--tweets')
        else:
            args.append('--stats')

        # args.append('--filter')

        ap = get_twint_arg_parser()
        arg = ap.parse_args(args)
        # arg.filter = filter_fn

        with open('tweets.txt', 'w+') as fp:
            with redirect_stdout(fp):
                twint.main(arg)

    def find_hashtag(self):
        # loc = self.api.trends_closest(*SAN_FRANCISCO)[0]
        # locid = loc['woeid']
        locid = UNITED_STATES_WOEID
        trends = [trend for trend in self.api.trends_place(locid)[0]['trends']
                  if trend['tweet_volume']]
        trends = sorted(trends, key=lambda t: t['tweet_volume'], reverse=True)
        topics = [trend['name'] for trend in trends if ' ' not in trend['name']]
        topic = random.choice(topics[:5])
        print('Popular topic/hashtag that was chosen is \'{}\''.format(topic))
        return topic

    def generate_tweet(self):
        corpus = load_corpus('tweets.txt')
        if corpus:
            tweet = self.markov(corpus)
            return tweet

        return None

    def markov(self, corpus):
        print('Using Markov Chains to generate tweets for hashtag...')
        text_model = POSifiedNewlineText(corpus, state_size=2)

        # tweets = []
        for _ in range(5):
            for _ in range(5):
                tweet = text_model.make_short_sentence(140)
                if tweet:

                    # gif_url = get_gif('cute bat')
                    # if gif_url:
                    #     tweet += ' ' + gif_url

                    break
            else:
                return None
            print(tweet)

        # ch = input('Press enter to post a tweet and continue!')
        return tweet

    def random_engagement(self, like=10, follow=5, retweet=0, new_corpus=True):
        print('Randomly engaging with the general population. #likes={}, #follows={}, #retweets={}'
              .format(like, follow, retweet))
        num_follows = num_retweets = 0
        def examine_candidate(tweetid, username, retweets, likes):
            nonlocal num_follows
            nonlocal num_retweets

            if num_retweets < retweet and high_popularity(retweets):
                try:
                    print('Retweeted tweet')
                    self.api.retweet(tweetid)
                    #time.sleep(20)
                    num_retweets += 1
                except:
                    pass

            if medium_popularity(likes):
                user_json = self.api.get_user(username)._json
                if (
                    not_bot(user_json) and
                    active_user(user_json) and
                    followback_user(user_json) and
                    likeback_user(user_json)
                   ):
                    if num_follows < follow and random.random() < 0.1:
                        print('Following user <{}>'.format(username))
                        self.follow(user_json['id'])
                        num_follows += 1
                        #time.sleep(20)

                    return True

            return False

        # Use twint to search for popular tweets of today/yester and randomly like a few
        if new_corpus:
            query = random.choice(QUERY_TERMS)
            self.generate_corpus(query, limit=30000, detail=True, old=True)

        parser = re.compile(
            r'(\d+) '     # Tweet ID
            r'[\d-]{10} '  # Date
            r'[\d:]{8} '   # Time
            r'[A-Z]+ '     # Timezone (e.g., UTC)
            r'<(\w+)> '      # Username
            r'.* '         # Tweet
            r'\| \d+ replies (\d+) retweets (\d+) likes')  # Statistics

        tweet_candidates = []
        with open('tweets.txt', 'r') as fp:
            for line in fp:
                if not line:
                    continue

                m = parser.match(line)
                if not m:
                    continue

                # tweetid, username, retweets, likes
                tweet = (m.group(1), m.group(2), int(m.group(3)), int(m.group(4)))

                if examine_candidate(*tweet):
                    tweet_candidates.append(tweet)

        print('Number of candidates: {}'.format(len(tweet_candidates)))
        if like and tweet_candidates:
            self.random_like(tweet_candidates, like)

    def random_like(self, candidates, like):
        tweets = random.sample(candidates, min(like, len(candidates)))
        for tweet in tweets:
            print('Randomly liked tweet with id {}...'.format(tweet[0]))
            self.like(tweet[0])
            #time.sleep(20)

    def like_back(self, userid):
        statuses = [status for status in self.api.user_timeline(userid, count=20)
                    if status._json['favorite_count'] >= 10]
        #time.sleep(20)
        for status in random.sample(statuses, min(4, len(statuses))):
            print('Liking back tweet from user with id {}...'.format(status._json['id']))
            try:
                self.like(status._json['id'])
            except:
                print('Failed to like back tweet with id {}'.format(status._json['id']))

    def like(self, tweetid):
        try:
            self.api.create_favorite(tweetid)
            time.sleep(20)
        except:
            print('Failed to like tweet with id {}'.format(tweetid))

    def tweet(self, query, new_corpus=True):
        def filter_tweet(tweet):
            text, *_ = tweet
            if not contains_one_of(text, FILTER_ITEMS):
                return True
            return False

        print('Trying to post a tweet for trending topic \'{}\''.format(query))
        if new_corpus:
            self.generate_corpus(query, filter_fn=filter_tweet)

        tweet = self.generate_tweet()
        if tweet:
            self.tweet_message(tweet)
            print('Posted tweet! Tweet: \'{}\''.format(tweet))
            return True
        else:
            print('No original tweets could be generated. Try again with a different hashtag!')
            return False

    def tweet_trendy(self, retries=5, new_corpus=True):
        for _ in range(retries):
            hashtag = self.find_hashtag()
            if self.tweet(hashtag, new_corpus):
                break

def medium_popularity(likes):
    return likes > 8 and likes < 80
def high_popularity(retweets):
    return retweets > 500
def active_user(user_json):
    return user_json['statuses_count'] > 1000
def followback_user(user_json):
    return (user_json['friends_count'] >= 0.6 * user_json['followers_count'] or
            user_json['followers_count'] > 3000000)
def likeback_user(user_json):
    return user_json['favourites_count'] > 500
def not_bot(user_json):
    return not contains_one_of(user_json['description'], BOT_DESC_ITEMS)
