import os
import numpy as np
from string import punctuation
from collections import Counter

import spacy
import nltk
from nltk import word_tokenize, ngrams
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.tag import perceptron

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer  #up-weights rare/distinctive words
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_selection import SelectKBest, chi2, f_classif, \
    f_regression, f_classif, mutual_info_classif

# download nltk data
nltk_data = {'stopwords': 'corpora/stopwords',
             'punkt': 'tokenizers/punkt',
             'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger'}

for pkg, path in nltk_data.items():
    try:
        nltk.data.find(path)
    except LookupError as e:
        print(e)
        nltk.download(pkg)

# "global" objects
sid = SentimentIntensityAnalyzer()
stopwords = set(stopwords.words('english'))
nlp = spacy.load('en_core_web_sm')
stemmer = SnowballStemmer('english')
translator = str.maketrans('', '', punctuation)
tagger = perceptron.PerceptronTagger()


def get_words_per_doc(txt):
    """
    Split text into words and count them.

    Parameters
    ----------
    txt : str
        Text string.

    Returns
    -------
    len : int
        Length of text string.
    """
    return len(txt.split())


def compute_sentiment(series, all=False):
    """
    Compute sentiment score for pd.Series. Can be applied to pd.DataFrame
    via .apply()

    Parameters
    ----------
    series : pd.Series
        Series of text snippets.

    all : bool
        If True, return compound sentiment score only. If False, return array
        of all four sentiment scores.

    Returns
    -------
    A series of sentiment score(s).
    """
    if all:
        return sid.polarity_scores(series)['compound']
    return sid.polarity_scores(series)

def normalize_text(text):
    """
    Process text to clean list of tokens.

    Parameters
    ----------
    text : str
        Input text/document.

    Returns
    -------
    Clean, stemmed list of tokens.
    """
    text = text.replace('\r', ' ').replace('\n', ' ')
    lower = text.lower()  # all lower case
    nopunc = lower.translate(translator)  # remove punctuation
    words = nopunc.split()  # split into tokens
    nostop = [w for w in words if w not in stopwords]  # remove stopwords
    no_numbers = [w if not w.isdigit() else '#' for w in nostop]  # normalize
    stemmed = [stemmer.stem(w) for w in no_numbers]  # stem each word
    return stemmed


def get_nouns_adj(text):
    """
    Compute number of nouns and adjectives in text.

    Parameters
    ----------
    text : str
        Input test/document.

    Returns
    -------
    Tuple of the number of nouns and adjectives.
    """
    tags = [x[1] for x in tagger.tag(word_tokenize(text))]
    num_nouns = len([t for t in tags if t[0] == 'N']) / len(tags)
    num_adj = len([t for t in tags if t[0] == 'J']) / len(tags)
    return num_nouns, num_adj
