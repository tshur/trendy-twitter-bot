import sys
import time
import argparse
import random

from utils import EmojiTranslator
from bot import TwitterBot


def get_twint_arg_parser():
    ap = argparse.ArgumentParser(prog="twint.py", usage="python3 %(prog)s [options]", description="TWINT - An Advanced Twitter Scraping Tool")
    ap.add_argument("-u", "--username", help="User's Tweets you want to scrape.")
    ap.add_argument("-s", "--search", help="Search for Tweets containing this word or phrase.")
    ap.add_argument("-g", "--geo", help="Search for geocoded tweets.")
    ap.add_argument("--near", help="Near a specified city.")
    ap.add_argument("--location", help="Show user's location (Experimental).", action="store_true")
    ap.add_argument("-l", "--lang", help="Serch for Tweets in a specific language")
    ap.add_argument("-o", "--output", help="Save output to a file.")
    ap.add_argument("-es", "--elasticsearch", help="Index to Elasticsearch")
    ap.add_argument("-t", "--timedelta", help="Time interval for every request")
    ap.add_argument("--year", help="Filter Tweets before specified year.")
    ap.add_argument("--since", help="Filter Tweets sent since date (Example: 2017-12-27).")
    ap.add_argument("--until", help="Filter Tweets sent until date (Example: 2017-12-27).")
    ap.add_argument("--fruit", help="Display 'low-hanging-fruit' Tweets.", action="store_true")
    ap.add_argument("--tweets", help="Display Tweets only.", action="store_true")
    ap.add_argument("--verified", help="Display Tweets only from verified users (Use with -s).", action="store_true")
    ap.add_argument("--users", help="Display users only (Use with -s).", action="store_true")
    ap.add_argument("--csv", help="Write as .csv file.", action="store_true")
    ap.add_argument("--json", help="Write as .json file.", action="store_true")
    ap.add_argument("--hashtags", help="Output hashtags in seperate column.", action="store_true")
    ap.add_argument("--userid", help="Twitter user id")
    ap.add_argument("--limit", help="Number of Tweets to pull (Increments of 20).")
    ap.add_argument("--count", help="Display number Tweets scraped at the end of session.", action="store_true")
    ap.add_argument("--stats", help="Show number of replies, retweets, and likes", action="store_true")
    ap.add_argument("--database", help="Store tweets in the database")
    ap.add_argument("--to", help="Search Tweets to a user")
    ap.add_argument("--all", help="Search all Tweets associated with a user")
    ap.add_argument("--followers", help="Scrape a person's followers", action="store_true")
    ap.add_argument("--following", help="Scrape who a person follows.", action="store_true")
    ap.add_argument("--favorites", help="Scrape Tweets a user has liked.", action="store_true")
    ap.add_argument("--debug", help="Debug mode", action="store_true")
    ap.add_argument("--proxy-type", help="Socks5, HTTP, etc.")
    ap.add_argument("--proxy-host", help="Proxy hostname or IP")
    ap.add_argument("--proxy-port", help="The port of the proxy server")
    return ap

if __name__ == '__main__':
    bot = TwitterBot()
    trans = EmojiTranslator()

    with open('botlog.txt', 'w') as fp:
        fp.write('Starting program loop...\n')

    i = 0
    while True:
        sys.stdout = open('botlog.txt', 'a')
        print('LOOP #{}'.format(i))

        if random.random() < 0.5:  # 30% chance to tweet
            print('TWEETING...')
            try:
                bot.tweet_trendy()
            except Exception as e:
                print('Error tweeting: {}'.format(e))

        try:
            bot.reciprocate()
        except Exception as e:
                print('Error reciprocating: {}'.format(e))

        if random.random() < 0.6:  # 50% chance to engage
            print('RANDOMLY ENGAGING...')
            try:
                bot.random_engagement(like=random.randint(10, 40),
                                      follow=random.randint(5, 20),
                                      retweet=1 if random.random() < 0.2 else 0)
            except Exception as e:
                print('Error randomly engaging: {}'.format(e))

        # Sleep randomly between 30min and 1 hour
        print('START SLEEPING\n')
        sys.stdout.close()
        time.sleep(60 * 30 * (random.random() + 1))
        i += 1
