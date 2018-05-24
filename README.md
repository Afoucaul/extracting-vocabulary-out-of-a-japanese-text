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

Example script (from [[1]](#robfahey)):

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


## Extracting segmented words out of an actual text

TODO: 
- pick an actual long text
- run mecab on it
- ignore useless words (`''`, `'。'`, `'！'`...)

## Getting the dictionary version of extracted words

Dictionary version := free from context


## References

- <a name="robfahey1"></a>[Japanese Text Analysis in Python](http://www.robfahey.co.uk/blog/japanese-text-analysis-in-python/)
- <a name="philipperemy1"></a>[Japanese Word2Vec](https://github.com/philipperemy/japanese-words-to-vectors)

