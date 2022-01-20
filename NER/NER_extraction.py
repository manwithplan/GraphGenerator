import spacy
from spacy.pipeline import EntityRuler
import pickle
import pickle
import tqdm
import pandas as pd
from collections import Counter


class NER:
    """
    class responsible for all Named Entity Recognition Operations
    """

    def __init__(self) -> None:
        # load the necessary data
        file = open("../stored_data/articles_cleaned.obj", "rb")
        self.articles_cleaned = pickle.load(file)
        file.close()

        file = open("../stored_data/company_tickers.obj", "rb")
        self.company_tickers = pickle.load(file)
        file.close()

        file = open("../stored_data/articles_with_tickers.obj", "rb")
        self.articles = pickle.load(file)
        file.close()

        file = open("../stored_data/commodities_list.obj", "rb")
        self.commodities_list = pickle.load(file)
        file.close()

        # set up a spacy language model
        self.nlp = spacy.load("en_core_web_lg")

        # get all the labels the pre-trained ner model can find
        self.entities = self.nlp.get_pipe("ner").labels

        # job titles that reference a person
        self.titles = [
            "minister",
            "governor",
            "president",
            "manager",
            "director",
            "sir",
            "secretary",
            "sheikh",
            "representative",
            "speaker",
            "representative",
            "deputy",
            "ceo",
        ]

        # company tickers that reference companies
        self.formatted_tickers = []

        for tick in self.company_tickers:
            self.formatted_tickers.append("lt;" + tick.lower())

        # set the entity types we will be looking for
        self.entity_type = [
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

    def extract_NER(self):
        """
        Responsible for extracting all the Named Entities from the dataset, it requires a configured language model in the model/ folder.
        """

        # load the language model
        self.nlp = spacy.load("../model/pipeline")

        # get the fileIDs as a list
        self.id = list(self.articles_cleaned.keys())

        # gather all entities from the text
        all_entities = dict((el, []) for el in self.entity_type)

        # store all articles in which the entity is named.
        entity_with_fileid = {}
        ent_to_article = {}

        for file_id in tqdm.tqdm(id):
            entity_with_fileid[file_id] = []
            article = self.articles_cleaned[file_id]

            # appy the model, and gather all entities we are looking for.
            doc = self.nlp(article)
            for ent in doc.ents:
                if (
                    (ent.label_ != "DATE")
                    and (ent.label_ != "CARDINAL")
                    and (ent.label_ != "PERCENT")
                    and (ent.label_ != "QUANTITY")
                    and (ent.label_ != "ORDINAL")
                    and (ent.label_ != "LANGUAGE")
                    and (ent.label_ != "MONEY")
                    and (ent.label_ != "TIME")
                ):
                    all_entities[ent.label_].append([ent.text, file_id])

        count = 0

        all_rows = []
        # for each type of entity
        for type in self.entity_type:
            selected_entities = all_entities[type]
            all_ents = []

            # store fileids with the entity
            for sel in selected_entities:
                ent = sel[0]
                all_ents.append(ent)
                id = sel[1]

                if ent in list(ent_to_article.keys()):
                    ent_to_article[ent].append(id)
                else:
                    ent_to_article[ent] = []
                    ent_to_article[ent].append(id)

            # and get the unique entities and their relevant information and store them in rows.
            counted_entities = Counter(all_ents)
            for key, val in counted_entities.items():
                count += 1
                articles = ent_to_article[key]
                row = [count, key, type, val, articles]
                all_rows.append(row)

        # format the extracted data into a dataframe and save it in a CSV file in the database folder
        entities = pd.DataFrame(
            all_rows, columns=["id", "name", "label", "mentions", "articles"]
        )
        entities.to_csv("../database/entities.csv")

    def setup_matcher(self):
        """
        Responsible for building the entity-ruler pipeline module we will be using
        """

        # define the custom patterns for person companies and commodities
        pattern_person = [
            {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "*"},
            {"IS_PUNCT": True, "OP": "?"},
            {"ORTH": {"IN": self.titles}},
            {"IS_PUNCT": True, "OP": "?"},
            {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "*"},
        ]

        pattern_company = [
            {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "*"},
            {"POS": "CCONJ"},
            {"ORTH": {"IN": self.formatted_tickers}},
            {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "*"},
        ]

        pattern_commodity = [{"ORTH": {"IN": self.commodities_list}}]

        patterns = [
            {"label": "PERSON", "pattern": pattern_person, "id": "Person of Interest"},
            {"label": "COMPANY", "pattern": pattern_company, "id": "Company"},
            {"label": "COMMODITY", "pattern": pattern_commodity, "id": "Comodity"},
        ]

        # build the custom pipeline component and add it to the pipeline.
        # Add it before the NER module to prevent overwriting other entity recognition.
        self.nlp = spacy.load("en_core_web_lg")

        ruler = EntityRuler(self.nlp)
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(patterns)

        # store the language model
        self.nlp.to_disk("../model/pipeline")
