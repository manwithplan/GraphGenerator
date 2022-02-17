import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

from neo4j import GraphDatabase, basic_auth

st.title("Named Entity Linking - Reuters")
st.write(
    "This is a web app to show relationships between entities detected in the Reuters dataset"
)

driver = GraphDatabase.driver(
    "bolt://localhost:7687", auth=basic_auth("neo4j", "NER123")
)

cypher_query = """
MATCH (n)
RETURN COUNT(n) AS count
LIMIT $limit
"""

nodes = []
edges = []

df_nodes = pd.read_csv()
df_rel = pd.read_csv()
# TODO add csv files for the graph.

for idx, item in df_nodes.iterrows():
    nodes.append(
        Node(id=item["node_id"], label=item["node_name"], NER=item["node_NER"])
    )

for idx, item in df_rel.iterrows():
    edges.append(
        Edge(source=item["Source"], target=item["Target"], label=item["Relationship"])
    )

# Configuration

config = Config(
    width=500,
    height=500,
    directed=True,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",  # or "blue"
    collapsible=True,
    node={"labelProperty": "label"},
    link={"labelProperty": "label", "renderLabel": True}
    # **kwargs e.g. node_size=1000 or node_color="blue"
)
return_value = agraph(nodes=nodes, edges=edges, config=config)
