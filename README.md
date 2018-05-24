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


## Extracting segmented words out of an actual text


## Getting the dictionary version of extracted words

Dictionary version := free from context


## References

- <a name="robfahey1"></a>[Japanese Text Analysis in Python](http://www.robfahey.co.uk/blog/japanese-text-analysis-in-python/)
