#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import traceback
from lib.information_extraction import parse_entities
from lib.kg_builder import build_graph 
from lib.text_cleaner import clean_text

def _search_entities(entities):
    return search_entities(entities)

def _clean_text(raw_text):
    return clean_text(raw_text)

def _build_graph(triplets, book_name):
    return build_graph(triplets, book_name)
    

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
        print (raw_text)
        f.close()

        # Clean text
        #raw_text = _clean_text(raw_text)

        # Information extraction
        # triplets = _parse_entities(raw_text)
        # if (triplets == None or len(triplets) < 1):
        #     print('No entities were found')
        triplets = []
        _build_graph(triplets, book_name)
        print('Entities were added to the knowledge graph')
    except Exception as e:
        traceback.print_exc()
        print (e)
        sys.exit(1)