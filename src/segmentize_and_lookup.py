#! /bin/env python3

import sys
import regex as re
import MeCab
import requests
import asyncio as aio

API_URL = "https://jisho.org/api/v1/search/words?keyword={}"

class ProgressBar:
    def __init__(self, high, size=50):
        self.high = high
        self.value = 0
        self.size = size

    def __str__(self):
        s = "|"
        s += ((20 * self.value) // self.high) * "█"
        s += ((20 * (self.high - self.value)) // self.high) * " "
        s += "|"
        s += " {}%".format(round(100 * self.value / self.high, 2))

        return s

    def increment(self):
        self.value += 1
        sys.stdout.write("\r{}".format(str(self)))
        sys.stdout.flush()
        

def validate_word(word):
    return (    
            not re.match(r'^\s*$', word)
            and not re.match(r'\W', word)
            and re.match(r'\p{Hiragana}|\p{Katakana}|\p{Han}', word)
            )


async def get_meaning(dictionary, word, progress_bar):
    data = requests.get(API_URL.format(word)).json()['data'][0]

    reading = data['japanese'][0]['reading']
    meanings = [x['english_definitions'][0] for x in data['senses']]

    dictionary[word] = {'reading': reading, 'meanings': meanings}

    progress_bar.increment()


async def main(meanings):
    words = set()
    wakati = MeCab.Tagger('-Owakati')
    with open(sys.argv[1], 'r') as file:
        content = file.read()
        words = {word for word in filter(
                validate_word,
                wakati.parse(content).split())}

    print("Extracted {} words".format(len(words)))

    progress_bar = ProgressBar(len(words))
    coroutines = [aio.create_task(get_meaning(meanings, word, progress_bar)) for word in words]
    await aio.wait(coroutines)
    print("\nDone.")


if __name__ == '__main__':
    event_loop = aio.get_event_loop()
    try:
        meanings = {}
        event_loop.run_until_complete(main(meanings))
        for word, data in meanings.items():
            print(word, data)

    finally:
        event_loop.close()
