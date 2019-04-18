import re
from html import unescape
import aiohttp
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode
import asyncio
import logging
import os

from networking import networking

STOP = set(stopwords.words("spanish")) - {"más", "menos"}
tokenizer = RegexpTokenizer(r"\w+")
dirname = os.path.dirname(__file__)
spanish_postagger = StanfordPOSTagger(
    os.path.join(dirname, 'models/spanish.tagger'), os.path.join(dirname, 'models/stanford-postagger.jar'), encoding='utf8')

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
           "Accept": "*/*",
           "Accept-Language": "es-MX,es;q=0.5",
           "Accept-Encoding": "gzip, deflate"}
GOOGLE_URL = "https://www.google.com.mx/search?q={}&ie=utf-8&oe=utf-8&client=firefox-b-1-ab"


def find_keywords(words):
    """
    Returns the list of words given without stopwords.
    :param words: List of words
    :return: Words without stopwords
    """
    return [w for w in tokenizer.tokenize(words.lower()) if w not in STOP]


def find_nouns(text, num_words, reverse=False):
    # manually remove '¿' symbol
    text = text.replace('¿', '')
    tokens = word_tokenize(text, language="spanish")
    print(tokens)

    tags = [tag for tag in spanish_postagger.tag(tokens) if tag[1] != 'POS']

    tags = tags[:num_words] if not reverse else tags[-num_words:]

    nouns = []
    consecutive_nouns = []

    for tag in tags:
        tag_type = tag[1]
        word = tag[0]

        if "nc" not in tag_type and len(consecutive_nouns) > 0:
            nouns.append(" ".join(consecutive_nouns))
            consecutive_nouns = []
        elif "nc" in tag_type:
            consecutive_nouns.append(word)

    if len(consecutive_nouns) > 0:
        nouns.append(" ".join(consecutive_nouns))
    return nouns


def find_q_word_location(question_lower):
    for q_word in ["que", "cuando", "quien", "cual", "donde", "por que", "como", "qué", "cuándo", "quién", "cuál", "dónde", "por qué", "cómo"]:
        q_word_location = question_lower.find(q_word)
        if q_word_location != -1:
            return q_word_location


def get_google_links(page, num_results):
    soup = BeautifulSoup(page, "html.parser")
    searchdiv = soup.find("div", {"id": "search"})
    results = searchdiv.findAll("div", {"class": "g"})
    # print(len(results))
    links = []
    for r in results:
        url = r.find("a")
        if url is not None:
            links.append(url["href"])
    # Remove duplicates while preserving order
    links = list(dict.fromkeys(links))
    return links[:num_results]


async def search_google(question, num_results):
    """
    Returns num_results urls from a google search of question.
    :param question: Question to search
    :param num_results: Number of results to return
    :return: List of length num_results of urls retrieved from the search
    """
    # Could use Google's Custom Search API here, limit of 100 queries per day
    # result = service.cse().list(q=question, cx=CSE_ID, num=num_results).execute()
    # return result["items"]
    page = await networking.get_response(GOOGLE_URL.format(question), timeout=4, myheaders=HEADERS)
    return get_google_links(page, num_results)


async def multiple_search(questions, num_results):
    queries = list(map(GOOGLE_URL.format, questions))
    pages = await networking.get_responses(queries, timeout=4, myheaders=HEADERS)
    link_list = [get_google_links(page, num_results) for page in pages]
    return link_list


def clean_html(html):
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"\n", " ", cleaned)
    cleaned = re.sub(r"\s\s+", " ", cleaned)
    return unidecode(unescape(cleaned.strip()))


async def get_clean_texts(urls, timeout=0.8, myheaders=HEADERS):
    responses = await networking.get_responses(urls, timeout, myheaders)
    return [clean_html(r).lower() for r in responses]
