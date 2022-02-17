

## Table of Contents
1. [Description](#description)
1. [Objectives](#objectives)
	1. [Challenges](#challenges)
	2. [Limitations](#limitations)
	3. [Further developments](#further-developments)
1. [Repo Architecture](#repo-architecture)
1. [Installation](#installation)
1. [Usage](#usage)
1. [Visuals](#visuals)
1. [Timeline](#timeline)
1. [Personal situation](#personal-situation)

## Description
This project is a part of the Becode.org AI Bootcamp programme. The goal is to provide a knowledge graph representing entities and relationships between them. Dataset: Reuters-21578 corpus.


<<<<<<< HEAD
<<<<<<< HEAD
improving the ruled based matching. Where it used to recognize between any 2 entities with a verb in the middle, it now only searches for entities in a certain list.

### version 1.2

applying manual and custom trained entity detection to all the dataset
=======
improving the ruled based matching. Where it used to recognize between any 2 entities with a verb in the middle, it now only searches for entities in a certain list.
>>>>>>> 9a9e105d3ff920b3d52f874cbaba108165336415
=======
## Objectives
- Be able to preprocess data obtained from textual sources
- Be able to employ named entity recognition and relationship extraction using spaCy
- Be able to visualize results
- Be able to present insights and findings to client
- Be able to store data using the graph database Neo4j
- Be able to write clean and documented code.

### Strengths
- Applicable for any text.
- Relationships are automatically extracted and clustered by meaning.
- Most modules are fully automated, some use context specific information that can be easily added.
- Entity Linking automatically groups entities that are spelled slightly different.
- Adaptable Neo4j graphs.

### Limitations
- Only a prototype of a graph in Streamlit developed.
- No transformers were harmed in the making of this project.

### Further Developments
- Implement interactive Streamlit app.
- Further automate Entity recognition.

## Repo Architecture
```
Project/
|-- Deployment/
|   |-- streamlit_app.py
|-- NER/
|   |-- NER_extraction.py
|-- Visualization/
|   |-- createGraph.py
|-- datacleaning/
|   |-- data_cleaning.py
|-- database/
|   |-- versions/
|   |   |-- v1.0
|   |   |-- v1.1
|   |   |-- v1.2
|   |   |-- v1.3
|   |-- entities.csv
|   |-- relationships.csv
|-- entity_linking/
|   |-- entityLinker.py
|   |-- entities_wiki_final.csv
|-- relationship_extraction/
|   |-- relationship_extraction.py
|-- stored_data/
|   |-- NER_train_data.obj
|   |-- all_verbs.obj
|   |-- articles_cleaned.obj
|   |-- articles_with_tickers.obj
|   |-- company_tickers.obj
|   |-- docs.obj
|   |-- entities.obj
|   |-- nouns.obj
|-- README.md
|-- .gitignore
|-- main.py
```

## Installation
- Clone the repository and install the dependencies with `requirements.txt`
- Run `main.py` to execute all the classes described in the Usage.
## Usage

### Data cleaning with RegEx
`data_cleaning/data_cleaning.py` contains a `Class get_data` that downloads the data and cleans it, using basic Python string manipulation.

### Named entity recognition with spaCy
`NER/NER_extraction.py ` contains a `Class NER` responsible for all named entity recognition operations, including extracting named entities from the dataset with a configured language model and an entity ruler pipeline. 

### Entity linking with Pywikibot
`entity_linking/entityLinker.py` contains a `Class entityLinker` responsible for linking the entities to wikipedia using the pywikibot library.

### Relationship extraction with spaCy
`relationship_extraction/relationship_extraction.py` contains a `Class relationshipExtraction` responsible for taking the previously found entities, and cross-referencing them with the database to find meaningful relations, including finding all the relationships by using the pattern matcher and using Jaccard similarity to make clusters from the verbs.

### Creating a graph database with Neo4j
`Visualization/createGraph.py` contains a `Class` responsible for connecting to a Neo4j database and uploading entities (as nodes) and relationships between them. 

### Deployment with Streamlit and Agraph
`Deployment/streamlit_app.py/` contains a prototype of a Streamlit app built with the Agraph component.
## Visuals

## Timeline
Duration: 2 weeks

### version 1.0 
We used the large english spacy nlp pipeline language model (*'en_core_web_lg'*) on cleaned data, using the in-built pre-trained NER model, 
ruled based matching between 2 entities with a verb in the middle for relationship extraction.

### version 1.1 
The ruled based matching was improved. Where it used to recognize between any 2 entities with a verb in the middle, it now only searches 
for entities specified in a certain list. A custom NER model was trained for data gathered in `PERSON`, `BANK`, `COMPANY`, `COMMODITY`, `AGREEMENTS`.

### version 1.2 
The custom NER model was discarded for poor performance and replaced with a custom entity ruler class looking for `COMPANY`, `PERSON` and `COMMODITY`.
Attempts at using Neural Coreference were discarded due to the constrained timing of the project.

### version 1.3
The relationship extraction was optimized by using a custom clustering algorithm. The application of entity linking links together identical entities 
with different syntax.

## Personal situation
Contributors: [manwithplan](https://github.com/manwithplan), [kpranke](https://github.com/kpranke)

**[Back to top](#table-of-contents)**
>>>>>>> 55a6acf7f76bbe583a74d012a2e218d95f8a5698
