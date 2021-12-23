"""
@author Group 17-Tong Wu(t3.wu@student.vu.nl 2734542)
@Create 18-12-2021 21:37 PM
OpenIE program for extracting entity relations in the book "Harry Potter and the Deathly Hallows"
StanfordCoreNLP-open ie execution
"""
from openie import StanfordOpenIE
import spacy


# https://stanfordnlp.github.io/CoreNLP/openie.html#api
# Default value of openie.affinity_probability_cap was 1/3.
properties = {
    'openie.affinity_probability_cap': 2 / 3,
}
triple_num = 0

try:
    nlp = spacy.load("en_core_web_md")
    nlp.max_length = 2000000
except:  # If they are not present, we must download
    spacy.cli.download("en")
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")


# use a string returned by text cleaner as variable
def spacy_ner(book_string):
    doc = nlp(book_string)
    ent_list = doc.ents
    return ent_list


def get_entity_list(ent_list):
    ent_text_list = []
    for ent in ent_list:
        if ent.text not in ent_text_list and ent.label_ == 'PERSON':
            ent_text_list.append(ent.text)
    return ent_text_list


def filter_relation(triple):
    bad_char = '’s'
    bad_quo = '’'
    relation_list = triple['relation'].split()
    if triple['relation'] != bad_char and bad_char in relation_list:
        relation_list.remove(bad_char)
        triple['relation'] = '_'.join(relation_list)
    elif triple['relation'] == bad_quo or triple['relation'] == '' or triple['relation'] == bad_char:
        triple['relation'] = ''
    elif bad_char not in relation_list:
        triple['relation'] = '_'.join(relation_list)
    return triple['relation'].upper()


def filter_relation_by_POS(triple):
    bad_char = '’s'
    bad_quo = '’'
    doc = nlp(triple['relation'].lower())
    relation_list = []
    accept_list = ['VERB', 'NOUN', 'PROPN', 'PART']
    for tok in doc:
        if tok.pos_ in accept_list and tok.text != 'is':
            relation_list.append(tok.lemma_) if tok.lemma_ != bad_quo else relation_list.append(bad_char)
        triple['relation'] = ' '.join(relation_list)
    return triple


def get_triples(start, end, book_text, entity_filter_list):
    with StanfordOpenIE(properties=properties) as client:
        corpus = book_text.replace('\n', ' ').replace('\r', '')
        """
        There are 812347 characters in the book, but there will 
        be jvm heap size error if process all characters one time,
        for now the maximum size of characters that we can put in 
        processing corpus is 300000 based on my testing
        """
        triples_corpus = client.annotate(corpus[start:end])
        triple_list = []
        final_triples = []
        for triple in triples_corpus:
            if triple['subject'] in entity_filter_list and triple['object'] in entity_filter_list:
                # filter relations
                triple = filter_relation_by_POS(triple)
                triple['relation'] = filter_relation(triple)
                if len(triple['relation']) != 0:
                    triple_list.append(triple)
        # remove duplicate triples from the triple_list
        tem_set = set()
        for tri in triple_list:
            t = tuple(tri.items())
            if t not in tem_set:
                tem_set.add(t)
                final_triples.append(tri)
    return final_triples


def generate_result(cleaned_text, entity_filter_list):
    final_triples = []
    num_of_characters = len(cleaned_text)
    times = num_of_characters // 100000
    if times != 0:
        for i in range(times + 1):
            start = i * 100000
            end = (i + 1) * 100000
            print("Start processing part %s of the book, totally %s characters" % (i + 1, end - start))
            current_len = len(final_triples)
            if end < num_of_characters:
                final_triples.extend(get_triples(start, end, cleaned_text, entity_filter_list))
            else:
                final_triples.extend(get_triples(start, num_of_characters, cleaned_text, entity_filter_list))
            print("Part %s are successfully process, %s relation triples are extracted" % (
                i + 1, len(final_triples) - current_len))
    else:
        final_triples.extend(get_triples(0, num_of_characters, cleaned_text, entity_filter_list))
    return final_triples


def parse_relation(cleaned_text):
    entities = spacy_ner(cleaned_text)
    entity_text_list = get_entity_list(entities)
    result = generate_result(cleaned_text, entity_text_list)
    return result


# relations = parse_relation("../books/stopwords_removed_Book.txt")

