import re
import nltk
import markovify
import requests
import random

from credentials import GIPHY_API_KEY

class POSifiedNewlineText(markovify.NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

class EmojiTranslator:
    def __init__(self):
        self.table_re = re.compile(r'(.+) (.+)', re.UNICODE)
        self.tag_re = re.compile(r'Emoji: (.+)')
        self.table = {}
        with open('emoji.txt', 'r') as fp:
            for line in fp:
                m = self.table_re.match(line)
                self.table[m.group(1)] = m.group(2)

    def encode(self, tag):
        m = self.tag_re.match(tag)
        if m:
            cldr = m.group(1).lower()
            if cldr in self.table:
                return self.table[cldr]

        return None

def get_gif(string):
    keywords = string.strip().split(' ')
    query = '+'.join(keywords)

    res = requests.get(url='http://api.giphy.com/v1/gifs/search?q={}&api_key={}&limit=10'.format(query, GIPHY_API_KEY))

    gifs = res.json()['data']
    gif = random.choice(gifs)
    url = gif['bitly_gif_url']
    return url

def contains_one_of(string, parts):
        for part in parts:
            if part in string:
                return True

        return False

def load_corpus(filename):
    num_lines = 0
    lines = []
    # pattern = re.compile(r'<Emoji: .*?>')
    with open(filename, 'r') as fp:
        for line in fp:
            line = re.sub(r'[<>]', '%%', line).strip()
            line = line.split('%%')
            result = []
            for term in line:
                if 'Emoji:' in term:
                    term = trans.encode(term)
                if not term or '.com' in term or '.ly' in term or '@' in term:
                    continue
                result.append(term)

            lines.append(' '.join(result))
            num_lines += 1

    if num_lines < 500:
        print('The corpus is not large enough to generate a good tweet!')
        return None

    return '\n'.join(lines)