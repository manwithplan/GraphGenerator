# Algorythm_NLP
Applying NLP to the full Reuters dataset


### version 1.0

standard spacy nlp pipeline, using pre trained NER model, ruled based matching between 2 entities with a verb in the middle and standard python string cleaning.

### version 1.1

improving the ruled based matching. Where it used to recognize between any 2 entities with a verb in the middle, it now only searches for entities in a certain list.