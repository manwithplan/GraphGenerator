import nltk
import pickle
import re


class get_data:
    """
    Class that downloads the data and cleans it, using basic python string manipulations.
    """

    def __init__(self, dataset=None) -> None:

        # download the dataset via the nltk lib
        nltk.download("reuters")
        nltk.download("punkt")
        from nltk.corpus import reuters

        self.reuters = reuters

        # variables for storing the files
        self.articles_cleaned = {}
        self.company_tickers = []
        self.files = reuters.fileids()

        self.suitable_articles, self.suitable_ids = self.select_suitable(
            self.files, self.reuters
        )

        if dataset != None:
            self.files = dataset
            self.suitable_articles = dataset

    def main(self):
        """
        Controlling function for this class. Stores python vars as pickle files in the stored_data folder
        """

        for idx, article in enumerate(self.suitable_articles):
            self.articles_cleaned[self.suitable_ids[idx]] = self.clean_articles(article)

        filehandler = open("../stored_data/articles_cleaned.obj", "wb")
        pickle.dump(self.articles_cleaned, filehandler)
        filehandler.close()

        filehandler = open("../stored_data/company_tickers.obj", "wb")
        pickle.dump(self.company_tickers, filehandler)
        filehandler.close()

    def select_suitable(self, files, reuters):
        """
        Select only the articles that are suitable for Natural Language Processing

        :returns: 2 lists, one containing the articles and one containing the ids
        """

        # Create empty vars for storing the id's and the articles.
        suitable_articles = []
        suitable_ids = []

        # filtering is done by counting the occurances of the string "vs"
        for article_id in files:
            if reuters.raw(article_id).count("vs") <= 1:
                suitable_articles.append(reuters.raw(article_id))
                suitable_ids.append(article_id)

        return [suitable_articles, suitable_ids]

    def clean_articles(self, article, company_tickers):
        """
        responsible for cleaning the articles.

        :article: takes in the raw input from the reuters dataset
        :company_tickers: store mentions of the company tickers to use them later on for recognizing the entities as companies
        :returns: a string representing the article
        """

        # First we extract the tickers from the text, they are formatted like "&lt;TICKER>"
        # We have to make an in-place company to keep track of th ones already found.
        tbc_article = article

        for i in range(tbc_article.count("&lt")):
            try:
                start = tbc_article.index("&lt")
                end = tbc_article.index(">")

                result = tbc_article[start + 4 : end]
                company_tickers.append(result)

                tbc_article = tbc_article.replace(tbc_article[start : end + 1], "")
            except:
                pass

        # on to the actual cleaning
        # replace newline staments
        txt_no_return = tbc_article.replace("\n", " ")

        # lowercase all tewt
        txt_lowered = txt_no_return.lower()

        # remove the ticker tags
        txt_no_lt = txt_lowered.replace("&lt", " ")

        # clean multiple spaces
        text_one_space = re.sub(" +", " ", txt_no_lt)

        # remove trailing and leading whitespaces
        text_clean = text_one_space.strip()

        return text_clean
