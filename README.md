# Extracting vocabulary out of a Japanese text

## Installing a lexical analyzer

Following [[1]](#robfahey1), I choose MeCab.

*This will clone the repo in the current directory, so take your time and be sure to put it where you want it to be*

```bash
sudo apt-get install mecab mecab-ipadic libmecab-dev mecab-ipadic-utf8 git curl
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd
sudo ./bin/install-mecab-ipadic-neologd -n
pip3 install mecab-python3
```

Example script from [[1]](#robfahey):

```python3
import MeCab

test = "今日はいい天気ですね。遊びに行かない？新宿で祭りがある！"
mt = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd")

parsed = mt.parseToNode(test)
components = []
while parsed:
    components.append(parsed.surface)
    parsed = parsed.next

print(components)
```

Output:

```python3
['', '', '', 'いい', '天気', 'です', 'ね', '。', '遊び', 'に', '行か', 'ない', '？', '新宿', 'で', '祭り', 'が', 'ある', '！', '']
```

The first three elements are empty strings, but these should clearly be respectively `'今'`, `'日'` and `'は'`.
What happened?
It turns out that MeCab is quite buggy with Python, crashing half of the time inconsistently, and skipping some words.

I decide to try with Nagisa.


### Kuromoji

Nagisa is a Python module, based on neural networks.
It's simply installed with `pip`, and can be tested easily:

```python3
In [1]: import nagisa
[dynet] random seed: 1234
[dynet] allocating memory: 512MB
[dynet] memory allocation done.

In [2]: nagisa.tagging("今日はいい天気ですね").words
Out[2]: ['今日', 'は', 'いい', '天気', 'です', 'ね']
```

It looks way better.
Maybe I'll have some surprises later on, but I'm pretty sure it's gonna be enough.

## Extracting segmented words out of an actual text

From now on, I'm sticking with Nagisa.

I'm now focusing on extracting all the words from an actual text.
The goal here is not to have these words in a plain form (辞書形); the issue related to forms will be handled later.

Let's test it on a more concrete file: [Wikipedia's article on Python, in Japanese](https://ja.wikipedia.org/wiki/Python).
I just made a Ctrl-A Ctrl-V of the page into a `python_wikipedia.txt` file, as all I need is a large amount of words.

I'm using the following script, to print out all the segmentized words from the input text:

```python3
# nagisa_segmentize.py

import nagisa
import sys

with open(sys.argv[1], 'r') as file:
    content = file.read()
    for word in nagisa.tagging(content).words:
        print(word)
```

Let's do this:

```shell
python3 nagisa_segmentize.py python_wikipedia.txt > output
```

The `output` file now contains more than 10,000 lines, and the beginning looks like this:

```shell
$ head -25 output 

	
Python


Jump
　
to
　
navigation
Jump
　
to
　
search


曖昧
さ
回避
　
	
この
項目
で
```

There are three issues to address, that are, from the easiest to the hardest:

1. There are empty words
2. There are duplicates
3. There are non-Japanese words


### Removing empty words

I will use for this purpose a simple regex, to remove both empty and all-blank words.
These days I'm found of functional programming, so I'm gonna use `filter`.
Here it is:

```python3
#! /bin/env python3

import sys
import re
import nagisa

with open(sys.argv[1], 'r') as file:
    content = file.read()
    for word in filter(
            lambda w: not re.match(r'^\s*$', w), 
            nagisa.tagging(content).words):
        print(word)
```

As expected, the empty words are filtered out.

I need to remove punctuation as well.
The `\W` regex metacharacter will help me out.
So I'm just adding a check against `r'\W'`, which represents a non-word character.
This way, I'll merely filter out any word that contains a non-word character.
This will include punctuation characters, but also potential weir results I'm not interested in.

```python3
#! /bin/env python3

import sys
import re
import nagisa

with open(sys.argv[1], 'r') as file:
    content = file.read()
    for word in filter(
            lambda w: not re.match(r'^\s*$', w) and not re.match(r'\W', w), 
            nagisa.tagging(content).words):
        print(word)

```

So here is the filtered output:

```shell
python3 nagisa_segmentize.py ../data/python_wikipedia.txt | head -25
[dynet] random seed: 1234
[dynet] allocating memory: 512MB
[dynet] memory allocation done.
Jump
to
navigation
Jump
to
search
曖昧
さ
回避
この
項目
で
は
プログラミング
言語
に
つい
て
説明
し
て
い
ます
その
他
```

### Removing the duplicates

To remove the duplicates, I'll simply convert the list into a set.
A set is a data structure that cannot contain duplicates, so the conversion will remove them.
Furthermore, I don't really need the words to be contained in a list, and a set should be enough, so I'll not convert the set back into a list.
Note however that this breaks the order, and I might need to fix this later.

I'll modify my script so as it puts the words into a set, and displays it at the end.

```python3
#! /bin/env python3

import sys
import re
import nagisa

words = set()

with open(sys.argv[1], 'r') as file:
    content = file.read()
    for word in filter(
            lambda w: not re.match(r'^\s*$', w) and not re.match(r'\W', w), 
            nagisa.tagging(content).words):
        words.add(word)

for word in words:
    print(word)
```

This is not really impressive, so I'm not gonna show the output here.


### Keeping only Japanese words

This is the tricky part.
I'm actually going to solve it in a very simple way, using Python's magic.
Regular expressions have a lot of metacharacter, but there's one that is less known that the rest: `\p`.
It allows to refer to a group of Unicode characters, called a Unicode category.
The categories that I am aiming for are `Hiragana`, `Katakana`, and `Han` (for kanjis, or hanzis in Mandarin Chinese) [[3]](#localizingjapan).

Unfortunately, Python's built-in module `re` does not support these categories.
But there exists a less known regular expression module for Python, called `regex` [[4]](#pythonregex).
This module handles a ridiculously broad range of ERE features, and provides `re`'s functions as well.

So using `regex` and the character categories, I'm just gonna filter out words that don't contain hiraganas, nor katakanas, nor kanjis.
This filtering might be a bit harsh, but it's gonna be good enough for now.

I'm going to write a `validate_word` function, so as to avoid writing all the filtering on a single line.

```python3
import regex as re

def validate_word(word):
    return (    
            not re.match(r'^\s*$', word)
            and not re.match(r'\W', word)
            and re.match(r'\p{Hiragana}|\p{Katakana}|\p{Han}', word)
            )
```

The main section of the script does not change a lot:

```python3
words = set()

with open(sys.argv[1], 'r') as file:
    content = file.read()
    for word in filter(
            validate_word,
            nagisa.tagging(content).words):
        words.add(word)

for word in words:
    print(word)
```

The output of this script is now only 1000 lines long, and contains only full Japanese words.

The goal of extracting a list of untouched words out of a text is now reached, although there might be some points to improve.
I will now focus on fetching the dictionary definitions for all these words.

## Getting the dictionary version of extracted words

In order to get the meaning of the extracted words, I will use Jisho website's API.
Jisho made a wonderful work, aggregating all the knowledge of Japanese language into a single website and a well-working API.
For each extracted word, I will send a request to this API with the module `requests`, and read the result.

The response received from Jisho's API will look like this:

```ipython
In [1]: import requests

In [2]: requests.get("https://jisho.org/api/v1/search/words?keyword=家").json()
Out[2]: 
{'data': [{'attribution': {'dbpedia': False,
    'jmdict': True,
    'jmnedict': False},
   'is_common': True,
   'japanese': [{'reading': 'いえ', 'word': '家'}],
   'senses': [{'antonyms': [],
     'english_definitions': ['house', 'residence', 'dwelling'],
     'info': [],
     'links': [],
     'parts_of_speech': ['Noun'],
     'restrictions': [],
     'see_also': [],
     'source': [],
     'tags': []},
    {'antonyms': [],
     'english_definitions': ['family', 'household'],
```

First, a function that gets the response for a single word:

```python3
import requests

def get_meaning(word):

```

Dictionary version := free from context


## Performance issues

- Compile the regexes beforehand
- Use generators instead of a list generation, to filter lazily


## References

- <a name="robfahey1"></a>[Japanese Text Analysis in Python](http://www.robfahey.co.uk/blog/japanese-text-analysis-in-python/)
- <a name="philipperemy1"></a>[Japanese Word2Vec](https://github.com/philipperemy/japanese-words-to-vectors)
- <a name="localizingjapan"></a>[Localizing Japan](http://www.localizingjapan.com/blog/2012/01/20/regular-expressions-for-japanese-text/)
- <a name="pythonregex"></a>[PyPI page on `regex` module](https://pypi.org/project/regex/)
- <a name="jisho"></a>[Jisho](https://jisho.org/)

