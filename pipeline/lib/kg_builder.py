# pip3 install neo4j-driver
from neo4j import GraphDatabase, basic_auth

try:
    NEO_HOST = os.environ['NEO_HOST']
    NEO_USER = os.environ['NEO_USER']
    NEO_PASS = os.environ['NEO_PASS']
except:
    NEO_HOST = "bolt://3.87.72.8:7687"
    NEO_USER = "neo4j"
    NEO_PASS = "cardboard-properties-beaches"

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
    triplets = [
        {
            'source': 'Harry Potter',
            'target': 'Ned Potter',
            'relationship': 'SON_OF'
        },
        {
            'source': 'Ned Potter',
            'target': 'Harry Potter',
            'relationship': 'FATHER_OF'
        },
        {
            'source': 'Harry Potter',
            'target': 'Bella Potter',
            'relationship': 'SON_OF'
        },
        {
            'source': 'Bella Potter',
            'target': 'Harry Potter',
            'relationship': 'MOTHER_OF'
        },
        {
            'source': 'Bella Potter',
            'target': 'Ned Potter',
            'relationship': 'MARRIED_TO'
        },
        {
            'source': 'Ned Potter',
            'target': 'Bella Potter',
            'relationship': 'MARRIED_TO'
        }
    ]
    prepared_triplets = []
    nodesPid = {}
    current_pid = 1
    for triplet in triplets:
        if triplet["source"] not in nodesPid:
            nodesPid[triplet["source"]] = current_pid
            current_pid += 1
        if triplet["target"] not in nodesPid:
            nodesPid[triplet["target"]] = current_pid
            current_pid += 1
        prepared_triplets.append({
            "source": triplet["source"],
            "target": triplet["target"],
            "relationship": triplet["relationship"],
            "source_pid": nodesPid[triplet["source"]],
            "target_pid": nodesPid[triplet["target"]],
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
                ids.append("a" + str(nodesPid[nodePid]) + ".pid = " + str(nodesPid[nodePid]) + " AND " + "a" + str(nodesPid[nodePid]) + '.book = "' + book_name + '"')      
            for i, rel in enumerate(chunk):
                n1 = "a" + str(rel["source_pid"])
                n2 = "a" + str(rel["target_pid"])
                rels.append("(" + n1 + ")-[r" + str(i) + ":" + rel["relationship"] + "]->(" + n2 + ")" )
            print ("""
                MATCH
                    """+ ",".join(characters) +"""
                WHERE """ + " AND ".join(ids) + """
                CREATE 
                    """ + ",".join(rels) +"""
            """)
            session.run("""
                MATCH
                    """+ ",".join(characters) +"""
                WHERE """ + " AND ".join(ids) + """
                CREATE 
                    """ + ",".join(rels) +"""
            """)

    driver.close()

if __name__ == '__main__':
    build_graph([], "Test Book 5")