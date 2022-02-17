from data_cleaning import data_cleaning
from NER import NER_extraction
from entity_linking import entityLinker
from relationship_extraction import relationship_extraction
from visualization import createGraph


class main:
    def __init__(self) -> None:
        self.cleaner = data_cleaning()
        self.NER_extr = NER_extraction()
        self.ent_link = entityLinker()
        self.rel_extr = relationship_extraction()
        self.viz = createGraph()

    def run(self):
        """
        Standard pipeling for creating a graph
        """
        # run the standard cleaning process
        self.cleaner.main()

        # setup and run NER extraction, for custom patterns edit self.NER_extr.patterns
        self.NER_extr.setup_matcher()
        self.NER_extr.extract_NER()

        # run the entity linking module
        self.ent_link.main()

        # extract, analyze and cluster the relations
        self.rel_extr.get_all_relationships()
        self.rel_extr.cluster_verbs()
        self.rel_extr.lookup_ids()
        self.rel_extr.relationship_tagger()

        # standard visualization, customiza using self.viz.add_edges/add_nodes/insert_data methods
        self.viz.create_main_graph()


if __name__ == "__main__":
    app = main()
    app.run()
