import pywikibot
import csv
import pandas as pd
import string


class entityLinker:
    """
    Class responsible for linking the entities to wikipedia using the pywikibot library
    """

    def __init__(self) -> None:
        # setup the pywikibot library
        self.site = pywikibot.Site("en", "wikipedia")

        # import the entities to be linked from the database
        self.df_entities = pd.read_csv("../database/entities.csv")

    def main(self):
        """
        main method running all entity linking
        """
        self.gather_entities()
        self.link_entities()

    def gather_entities(self):
        """
        Method responisble for the actual linking
        """

        # initialize vars
        entities_wiki = []

        # for each row in the library
        for idx, row in self.df_entities.iterrows():

            # Apply some preprocessing, to improve the API lookup
            entity = row["name"].replace("the", "").title()
            entity = entity.translate(str.maketrans("", "", string.punctuation))
            label = row["label"]
            id = row["id"]

            # attempt a lookup and store the result in the entities_wiki object
            try:
                page = pywikibot.Page(self.site, entity)
                item = pywikibot.ItemPage.fromPage(page)
                entities_wiki.append([id, entity, item, label])
                print(idx, "out of" "24304")
            except:
                entities_wiki.append([id, entity, None, label])

        # store the results in a dataframe to be cleaned
        self.df = pd.DataFrame(entities_wiki)

        try:
            # format the columns
            self.df.drop("Unnamed: 0", axis=1, inplace=True)
        except KeyError:
            pass
        self.df = self.df.rename(
            {"0": "id", "1": "entity", "2": "wiki_code", "3": "label"}, axis=1
        )

    def link_entities(self):
        """
        Method responsible for linking the actual entities
        """

        # create new column for deduplicated ids
        id_dedup = []

        # make a dict for finding previously matched links recursively. This is necessary to group the ids together.
        wiki_codes = {}
        for idx, row in self.df.iterrows():
            if isinstance(row["wiki_code"], float):
                id_dedup.append(row["id"])
            else:
                if row["wiki_code"] in wiki_codes.keys():
                    id_dedup.append(wiki_codes[row["wiki_code"]])
                else:
                    wiki_codes[row["wiki_code"]] = row["id"]
                    id_dedup.append(row["id"])

        # add column to dataframe and save it to the database
        self.df["id_dedup"] = id_dedup
        self.df.to_csv("entities_wiki_final.csv")
        self.df.to_csv("../database/entities.csv")
