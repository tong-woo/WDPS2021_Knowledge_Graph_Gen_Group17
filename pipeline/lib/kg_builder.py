# pip3 install neo4j-driver
from neo4j import GraphDatabase, basic_auth


def get_graph_n_nodes(triplets, book_name):
    driver = GraphDatabase.driver(
        "bolt://3.87.72.8:7687",
        auth=basic_auth("neo4j", "cardboard-properties-beaches"))

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
    # Need to add a unique ID to each node (source + target) in the array
    # Need to add book name to each node in the array

    # Need to add unique ID to each node, and need to add book name to each node in the query
    # Check if this works
    with driver.session() as session:
        session.run("""
            UNWIND $data as row
            MERGE (c:Character{name:row.source})
            MERGE (t:Character{name:row.target})
            MERGE (c)-[i:row.relation]->(t)
        """, {'data': data})