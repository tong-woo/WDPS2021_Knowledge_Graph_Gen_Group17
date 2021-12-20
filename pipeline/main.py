#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import traceback
from lib.information_extraction import parse_entities
from lib.kg_builder import build_graph 
from lib.text_cleaner import clean_text

OUTPUT_FILE = "sample_predictions.tsv"


def _search_entities(entities):
    return search_entities(entities)

def _clean_text(raw_text):
    return clean_text(raw_text)

def _build_graph(triplets, book_name):
    return build_graph(triplets, book_name)
    

if __name__ == '__main__':
    import sys
    try:
        _, INPUT = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    try:
        # Get book name 
        book_name = input('Input a name for this book: ')
        book_name = book_name.strip().replace("\n", "").replace("\t", "")

        # Get text of book from file
        f = open(INPUT, 'r')
        raw_text = " ".join(f.readlines())
        f.close()

        # Clean text
        raw_text = _clean_text(raw_text)

        # Information extraction
        triplets = _parse_entities(raw_text)
        if (triplets == None or len(triplets) < 1):
            print('No entities were found')

        _build_graph(triplets, book_name)

    except Exception as e:
        traceback.print_exc()
        print (e)

    print('Entities were added to the knowledge graph')