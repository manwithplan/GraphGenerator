import spacy
from spacy.tokens import Token
from spacy.matcher import Matcher
from spacy import displacy
import pandas as pd
import pickle
import random
import tqdm
import numpy as np
from nltk.corpus import wordnet


class relationshipExtraction:
    """
    class responsible for taking the previously found entities, and cross-referencing them with the database to find meaningful relations
    """

    def __init__(self) -> None:
        # initialize vars
        self.all_verbs = []
        self.e2e_relationship = []

        # load in the necessary data
        file = open("../stored_data/articles_with_tickers.obj", "rb")
        self.docs = pickle.load(file)
        file.close()

        # load the language model
        self.nlp = spacy.load("../model/pipeline")

        # define the entities we will be looking at
        self.filtered_entities = [
            "EVENT",
            "FAC",
            "GPE",
            "LAW",
            "LOC",
            "NORP",
            "ORG",
            "PERSON",
            "PRODUCT",
            "WORK_OF_ART",
            "COMPANY",
            "COMMODITY",
        ]

    def get_all_relationships(self):
        """
        function responsible for finding all the relationships by using the pattern matcher
        """

        # set up new matcher object
        matcher = Matcher(self.nlp.vocab)

        # setup patter that scouts for a verb between 2 entities
        pattern = [
            {"ENT_TYPE": {"IN": self.filtered_entities}},
            {"ENT_TYPE": {"NOT_IN": self.filtered_entities}, "OP": "*"},
            {"POS": "VERB"},
            {"ENT_TYPE": {"NOT_IN": self.filtered_entities}, "OP": "*"},
            {"ENT_TYPE": {"IN": self.filtered_entities}},
        ]
        matcher.add("any_verb", [pattern])

        # loop over the articles
        for id, file in tqdm.tqdm(self.docs.items()):

            # and apply the custom pipeline
            doc = self.nlp(file)

            # also apply the matcher
            matches = matcher(doc)

            for match_id, start, end in matches:
                span = doc[start:end]

                # detect whether verbs are used in passive sense, in which case we wil switch subj and obj dependencies
                is_passive = False

                # gather the verbs
                for token in span:
                    if token.pos_ == "VERB":
                        verb = token.lemma_
                        self.all_verbs.append(token)
                    if "pass" in token.dep_:
                        is_passive = True

                # gather the subject and objects
                if is_passive:
                    for token in span:
                        if "subjpass" in token.dep_:
                            obj = token
                            obj_ent = token.ent_type_
                        elif "obj" in token.dep_:
                            subj = token
                            subj_ent = token.ent_type_
                else:
                    for token in span:
                        if "obj" in token.dep_:
                            obj = token
                            obj_ent = token.ent_type_
                        elif "subj" in token.dep_:
                            subj = token
                            subj_ent = token.ent_type_

                self.e2e_relationship.append([subj, subj_ent, verb, obj, obj_ent])

        # remove all bad matches
        e2e_relationship_clean = []

        for rel in self.e2e_relationship:
            if (rel[1] != "") and (rel[-1] != ""):
                e2e_relationship_clean.append(rel)

        self.e2e_relationship = e2e_relationship_clean

        self.df = pd.DataFrame(
            self.e2e_relationship,
            columns=["subj", "subj_label", "verb", "obj", "obj_label"],
        )

    def cluster_verbs(self):
        """
        method that uses Jaccard similarity to make clusters from the verbs
        """
        self.lookup_synonyms()
        self.generate_cluster()

        thresh = 0.4
        results_clusters = self.jaccard_clustering(self.only_cluster, thresh)

    def lookup_synonyms(self):
        """
        Using the in-built wordnets from nltk, this method finds the synonyms to the verbs.
        """
        self.synonyms = []
        self.dictSynonyms = {}

        self.synonyms = [[] for x in range(len(set(self.used_verbs)))]

        for idx, verb in enumerate(set(self.used_verbs)):

            self.dictSynonyms[verb] = []

            for syn in wordnet.synsets(verb):
                for l in syn.lemmas():
                    self.dictSynonyms[verb].append(l.name())
                    self.synonyms[idx].append(l.name())

    def generate_cluster(self):
        """
        Build the original clusters to optimize from the synonymns that we have found in the lookup_synonyms method
        """

        clusters = {}
        self.only_cluster = []

        for idx, verb_1 in enumerate(list(set(self.used_verbs))):
            print(idx, len(set(self.used_verbs)), end="\r")

            clusters[verb_1] = []

            for verb_2 in list(set(self.used_verbs)):

                if verb_2 in self.dictSynonyms[verb_1]:
                    clusters[verb_1].append(verb_2)

        for key, cluster in clusters.items():
            self.only_cluster.append(cluster)

    def jaccard_similarity(self, list1, list2):
        """
        Helper function for calculating Jaccard similarity metric
        :list1: List containing synonyms
        :list2: List containing synonyms
        :return: a float representing similarity between the 2 lists
        """
        s1 = set(list1)
        s2 = set(list2)
        return float(len(s1.intersection(s2)) / len(s1.union(s2)))

    def generate_self_similarity_matrix(self, cluster_lists):
        """
        Generate a n*n matrix from a list of n clusters. the matrix is filled with Jaccard similarity scores.

        :cluster_lists: Takes in a list of lists containing different words.
        :returns: a distance matrix based on Jaccard
        """

        count = 0

        self_similarity_matrix = [[] for x in range(len(cluster_lists))]

        for cluster_1 in cluster_lists:
            for cluster_2 in cluster_lists:
                try:
                    self_similarity_matrix[count].append(
                        self.jaccard_similarity(cluster_1, cluster_2)
                    )
                except ZeroDivisionError:
                    self_similarity_matrix[count].append([])

            count += 1

        return self_similarity_matrix

    def jaccard_clustering(self, clustered_list, thresh):
        """
        method for building the actual clusters
        :clustered_list: original list of synonyms
        :thresh: float between 0.0 and 1.0, representing threshold for Jaccard cut-off
        :return: new clusters where the clusters are bigger and containing more synonyms
        """

        clustered_results = []

        self_similarity_matrix = self.generate_self_similarity_matrix(clustered_list)

        for id, row in enumerate(self_similarity_matrix):

            indices = []
            for val in row:
                try:
                    if (val >= thresh) and (val != 1.0):
                        indices.append(row.index(val))
                except:
                    pass

            result = [clustered_list[y] for y in indices]
            if result == []:
                clustered_results.append(list(set(clustered_list[id])))
            else:
                clustered_results.append(
                    list(set([item for sublist in result for item in sublist]))
                )

        return clustered_results

    def relationship_tagger(self):
        """
        Method that looks up the verbs in the custom built clusters.
        By always selecting the first match going from large to small we increase continuity.
        """
        self.relationship_db = {"undefined": []}

        count = 0
        for x in self.results_clusters:
            if len(x) > 1:
                count += 1
                self.relationship_db[x[0]] = x
            else:
                self.relationship_db["undefined"].append(x)

        self.relationships = []

        for idx, row in self.df.iterrows():
            found = False
            for key, cluster in self.relationship_db.items():
                if (row["verb"] in cluster) and (found == False):
                    found = True
                    res = key

            if not res:
                res = "None"

            self.relationships.append(res)

            self.df["relationship"] = self.relationships
            self.df.to_csv("../database/relationships.csv")

    def lookup_ids(self):
        """
        Method that looks up the ids for the entities found.
        """

        df_id = pd.read_csv("../database/entities.csv")

        # cross reference the entities with the entity database for storing with the proper ids.
        subj_idx = []
        obj_idx = []

        for idx, row in self.df.iterrows():
            subj = row["subj"].text.lower()
            obj = row["obj"].text.lower()

            idx = df_id.loc[df_id.name == subj]["id"].values
            try:
                idx = idx[0]
            except IndexError:
                idx = np.nan

            subj_idx.append(idx)

            idx = df_id.loc[df_id.name == obj]["id"].values
            try:
                idx = idx[0]
            except IndexError:
                idx = np.nan
            obj_idx.append(idx)

        self.df["subj_id"] = subj_idx
        self.df["obj_id"] = obj_idx

        # store the relationships with the ids in the correct db
        self.df.to_csv("../database/relationships.csv")
        self.df = pd.read_csv("../database/relationships.csv", index_col=0)
        self.df = self.df.dropna()
        self.df = self.df.astype({"subj_id": int, "obj_id": int})
        self.df.to_csv("../database/relationships.csv")
        self.used_verbs = self.df["verb"].to_list()
