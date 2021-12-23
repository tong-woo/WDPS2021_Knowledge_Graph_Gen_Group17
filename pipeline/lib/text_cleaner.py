from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import requests


def stopwords_removal(raw_text):
    stopwords_list = requests.get("https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw"
                                  "/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt").content
    stop_words_2 = set(stopwords_list.decode().splitlines())
    stop_words_1 = set(stopwords.words('english'))
    # word_tokenize accepts
    # a string as an input, not a file.
    stop_word_list = stop_words_1 | stop_words_2

    # file1 = open("Harry Potter and the Deathly Hallows.txt")

    # Use this to read file content as a stream output and output a stop-words removed book
    # line = text.read()
    words = [word for word in raw_text.split() if word.lower() not in stop_word_list]
    return " ".join(words)


def clean_text(raw_text):
    text = ""
    try:
        text = stopwords_removal(raw_text)
    except Exception as e:
        print("Catched exception", e)
    return text
