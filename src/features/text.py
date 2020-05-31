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

from gensim.utils import simple_preprocess

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

LANGUAGE = 'english'

# "global" objects
sid = SentimentIntensityAnalyzer()
stopwords = set(stopwords.words(LANGUAGE))
NLP = spacy.load('en_core_web_sm')
stemmer = SnowballStemmer(LANGUAGE)
translator = str.maketrans('', '', punctuation)
tagger = perceptron.PerceptronTagger()


def connect_tokens(list_of_tokens):
    """join token list itmes separated by whitespace"""
    return " ".join(list_of_tokens)


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


def compute_sentiments(text, all_scores=True):
    """
    Compute sentiment score for text. Can be applied to pd.DataFrame
    via .apply()

    Parameters
    ----------
    text : str
        Text snippet.

    all_scores : bool
        If False, return compound sentiment score only. If True, return dict
        with all four sentiment scores.

    Returns
    -------
    Sentiment scores as tuple of ('neg', 'neu', 'pos', 'compound')
    """
    sentiments = sid.polarity_scores(text)
    sentiment_scores = tuple(sentiments.values())

    if all_scores:
        return sentiment_scores
    else:
        return sentiment_scores[3]


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


def preprocess_spacy(text):
    """Apply spacy preprocessing pipeline. Return clean tokens"""
    doc = NLP(text)
    #return [token.text for token in doc]
    return list(doc.sents)


def preprocess_gensim(text):
    return simple_preprocess(text)


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