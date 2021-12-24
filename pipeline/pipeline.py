#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import traceback
from lib.information_extraction import parse_relation
from lib.kg_builder import build_graph
from lib.text_cleaner import clean_text


def _parse_relation(cleaned_text):
    return parse_relation(cleaned_text)


def _clean_text(raw_text):
    return clean_text(raw_text)


def _build_graph(triplets, book_name):
    return build_graph(triplets, book_name)

# python ./pipeline.py "./books/book.txt" "Test Book 1"
if __name__ == '__main__':
    import sys

    try:
        _, INPUT, book_name = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    try:
        # Get text of book from file
        f = open(INPUT, 'r')
        raw_text = " ".join(f.readlines())
        print("File opened successfully!")
        f.close()

        # Clean text
        cleaned_text = _clean_text(raw_text)
        print('Stopwords removed!')

        # Information extraction
        triplets = _parse_relation(cleaned_text)
        for item in triplets:
            print(item)
        print('Found %s triples in the filtered corpus.\n' % len(triplets))


        if (triplets == None or len(triplets) < 1):
            print('No person reletions were found')

        _build_graph(triplets, book_name)

    except Exception as e:
        traceback.print_exc()
        print(e)
        sys.exit(1)
