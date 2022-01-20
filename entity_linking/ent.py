import pywikibot
import csv
import pandas as pd
import string

site = pywikibot.Site("en", "wikipedia")

df_entities = pd.read_csv("../database/entities.csv")

entities_wiki = []
field_names = ["entity", "item", "NER"]
for idx, row in df_entities.iterrows():
    entity = row["name"].replace("the", "").title()
    entity = entity.translate(str.maketrans("", "", string.punctuation))
    label = row["label"]
    id = row["id"]
    try:
        page = pywikibot.Page(site, entity).get(throttle=False)
        item = pywikibot.ItemPage.fromPage(page)
        entities_wiki.append([id, entity, item, label])
        print(idx, "out of" "24304")
    except:
        entities_wiki.append([id, entity, None, label])

df = pd.DataFrame(entities_wiki)
# df.to_csv('entities_wiki_v2.csv')
# df = pd.read_csv('entities_wiki_v2.csv')
print(df)
df.drop("Unnamed: 0", axis=1, inplace=True)


df = df.rename({"0": "id", "1": "entity", "2": "wiki_code", "3": "label"}, axis=1)

id_dedup = []
wiki_codes = {}
for idx, row in df.iterrows():
    try:
        if isinstance(row["wiki_code"], float):
            id_dedup.append(row["id"])
        else:
            if row["wiki_code"] in wiki_codes.keys():
                id_dedup.append(wiki_codes[row["wiki_code"]])
            else:
                wiki_codes[row["wiki_code"]] = row["id"]
                id_dedup.append(row["id"])
    except KeyError:
        id_dedup.append("None")
        print("None")

df["id_dedup"] = id_dedup
df.to_csv("entities_wiki_final.csv")
