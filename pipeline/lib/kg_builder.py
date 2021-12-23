# pip3 install neo4j-driver
import string

from neo4j import GraphDatabase, basic_auth
import os

try:
    NEO_HOST = os.environ['NEO_HOST']
    NEO_USER = os.environ['NEO_USER']
    NEO_PASS = os.environ['NEO_PASS']
except:
    NEO_HOST = "bolt://100.26.187.245:7687"
    NEO_USER = "neo4j"
    NEO_PASS = "driller-data-plant"

driver = GraphDatabase.driver(
    NEO_HOST,
    auth=basic_auth(NEO_USER, NEO_PASS))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_graph_n_nodes(triplets, book_name):
    with driver.session(database="neo4j") as session:
        results = session.read_transaction(
            lambda tx: tx.run(cypher_query).data())
        for record in results:
            print(record['count'])
    driver.close()


def build_graph(triplets, book_name):
    prepared_triplets = []
    nodesPid = {}
    current_pid = 1
    for triplet in triplets:
        if triplet["subject"] not in nodesPid:
            nodesPid[triplet["subject"]] = current_pid
            current_pid += 1
        if triplet["object"] not in nodesPid:
            nodesPid[triplet["object"]] = current_pid
            current_pid += 1
        prepared_triplets.append({
            "source": triplet["subject"],
            "target": triplet["object"],
            "relationship": triplet["relation"],
            "source_pid": nodesPid[triplet["subject"]],
            "target_pid": nodesPid[triplet["object"]],
            "book": book_name
        })

    with driver.session(database="neo4j") as session:
        session.run("""
            UNWIND $data as row
            MERGE (c:Character{name:row.source, book:row.book, pid:row.source_pid})
            MERGE (t:Character{name:row.target, book:row.book, pid:row.target_pid})
        """, {'data': prepared_triplets})

        for chunk in chunks(prepared_triplets, 100):
            characters = []
            ids = []
            rels = []
            mapping = {}
            for nodePid in nodesPid.keys():
                characters.append("(a" + str(nodesPid[nodePid]) + ":Character)")
                ids.append("a" + str(nodesPid[nodePid]) + ".pid = " + str(nodesPid[nodePid]) + " AND " + "a" + str(
                    nodesPid[nodePid]) + '.book = "' + book_name + '"')
            for i, rel in enumerate(chunk):
                n1 = "a" + str(rel["source_pid"])
                n2 = "a" + str(rel["target_pid"])
                rels.append("(" + n1 + ")-[r" + str(i) + ":" + rel["relationship"] + "]->(" + n2 + ")")
            print("""
                MATCH
                    """ + ",".join(characters) + """
                WHERE """ + " AND ".join(ids) + """
                CREATE 
                    """ + ",".join(rels) + """
            """)
            session.run("""
                MATCH
                    """ + ",".join(characters) + """
                WHERE """ + " AND ".join(ids) + """
                CREATE 
                    """ + ",".join(rels) + """
            """)

    driver.close()

# .replace("’", "").replace("]", "").translate(str.maketrans('', '', string.punctuation))
