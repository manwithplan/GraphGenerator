from neo4j import GraphDatabase
import pandas as pd
import time


class createGraph:
    def __init__(self) -> None:
        # create connection to the db
        self.conn = Neo4jConnection(
            uri="bolt://localhost:7687", user="neo4j", pwd="NER123"
        )
        self.conn.query(
            "CREATE CONSTRAINT UniqueEntityId ON (n:Node) ASSERT n.id IS UNIQUE"
        )

        # import database
        self.df_nodes = pd.read_csv("../database/entities.csv")
        self.df_nodes["label"] = self.df_nodes["label"].apply(lambda label: [label])
        self.df_rel = pd.read_csv("../database/relationships.csv")

    def create_main_graph(self):
        """
        function that loads the full dataset
        """

        self.add_nodes(self.df_nodes)

        for relationship in self.df_rel["relationship"].unique():
            print(relationship)
            y = self.df_rel[self.df_rel["relationship"] == relationship]
            # print(y.shape)
            self.add_edges(y)

    def add_nodes(self, rows):
        """
        Build nodes for the entities in the database

        :rows: dataframe row input
        :return: function callback for inserting data into the neo4j graph
        """

        query = """ UNWIND $rows AS row
                    MERGE (:Node {name: row.name, id: row.id, type: row.label})
                    RETURN count(*) as total
        """
        return self.insert_data(query, rows)

    def add_edges(self, rows):
        """
        Connect the nodes based on the established relations in the relations database

        :rows: dataframe row input
        :return: function callback for inserting data into the neo4j graph
        """

        query = (
            """ UNWIND $rows AS row
                    MATCH (src:Node {id: row.subj_id}), (tar:Node {id: row.obj_id})
                    CREATE (src)-[rel:%s]->(tar)
        """
            % relationship
        )

        return insert_data(query, rows)

    def insert_data(self, query, rows):
        """
        Insert formatted data in the Neo4j database

        :query: CYPHER code for the query
        :rows: dataframe row input
        :return: formatted input to the database
        """
        total = 0
        start = time.time()
        result = None

        res = self.conn.query(query, parameters={"rows": rows.to_dict("records")})
        try:
            total = res[0]["total"]
        except:
            total = 0
        result = {"total": total, "time": time.time() - start}
        print(result)

        return result

    def add_label_query(self):
        """
        Update node labels based on node_NER list. Can run in the neo4j terminal.

        :return: CYPHER query for adding labels to the nodes
        """
        query = """
            MATCH (n:Node) 
            CALL apoc.create.addLabels(n, n.type) 
            YIELD node 
            RETURN node
            """

        return query


class Neo4jConnection:
    """
    Class responsible for creating a Neo4J graph from the generated csv files
    """

    def __init__(self, uri, user, pwd):
        # set up connection details
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None

        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        """
        Method for closing the driver
        """

        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        """
        method for executing queries.
        :query: query in formatted string that represent CYPHER code
        :parameters: (optional) parameters for query execution
        :db: (optional) selection of the database
        :return: standard neo4J response protocol message
        """

        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None

        try:
            session = (
                self.__driver.session(database=db)
                if db is not None
                else self.__driver.session()
            )
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response
