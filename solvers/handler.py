import itertools
import re
import time
from collections import defaultdict
from unidecode import unidecode
import colorama
from colorama import Fore, Back, Style
import difflib

from solvers import search

punctuation_to_none = str.maketrans(
    {key: None for key in "¡!\"#$%&'()*+,-.:;<=>¿?@[\\]^_`{|}~�"})
punctuation_to_space = str.maketrans(
    {key: " " for key in "¡!\"#$%&'()*+,-.:;<=>¿?@[\\]^_`{|}~�"})

# TODO: Metodo 0 de busqueda directa en la pagina de resultados de google
#      tal vez busqueda en twitter y/o bing


async def answer_question(myquestion, original_answers):
    question = myquestion
    millisstart = int(round(time.time() * 1000))

    answers = []
    for ans in original_answers:
        # answers.append(unidecode(ans.translate(punctuation_to_none)))
        answers.append(unidecode(ans.translate(punctuation_to_space)))

    answers = list(dict.fromkeys(answers))
    question_lower = question.lower()

    reverse = "NO" in question or "NUNCA" in question
    # ("menos" in question_lower and "al menos" not in question_lower) or\

    # Get all words in quotes
    quoted = re.findall(r'"([^"]*)"', question_lower)
    no_quote = question_lower
    for quote in quoted:
        no_quote = no_quote.replace(f"\"{quote}\"", "1placeholder1")

    question_keywords = search.find_keywords(no_quote)

    for quote in quoted:
        quote = quote.replace('  ', ' ')
        question_keywords[question_keywords.index(
            "1placeholder1")] = quote.replace(' ', '+').replace('  ', ' ')
    search_results = await search.search_google("+".join(question_keywords), 5)
    search_text = [x.translate(punctuation_to_none) for x in await search.get_clean_texts(search_results)]
    best_answer = await __search_method1(search_text, answers, reverse)
    if best_answer == "":
        best_answer = await __search_method2(search_text, answers, reverse)
    # best_answer = ""  # REMOVE QUICKLY
    if best_answer == "":
        # Get key nouns for Method 3
        key_nouns = set(quoted)

        q_word_location = search.find_q_word_location(question_lower)
        if len(key_nouns) == 0:
            if q_word_location > len(question) // 2 or q_word_location == -1:
                key_nouns.update(search.find_nouns(question, num_words=8))
            else:
                key_nouns.update(search.find_nouns(
                    question, num_words=6, reverse=True))

        # Add consecutive capitalised words (Thanks talentoscope!)
        key_nouns.update(re.findall(r"([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)",
                                    " ".join([w for idx, w in enumerate(question.split(" ")) if idx != q_word_location])))

        key_nouns = {noun.lower() for noun in key_nouns}
        #print("keynouns: ")
        # print(key_nouns)
        best_answer = await __search_method3(list(set(question_keywords)), key_nouns, original_answers, reverse)

    # Search proposed answer in original answers list
    best_answer = difflib.get_close_matches(
        best_answer, original_answers, 1, 0.7)[0]

    print(Fore.YELLOW + f"PREGUNTA: {myquestion}")
    print(Fore.GREEN + f"RESPUESTA: {best_answer}")
    millisend = int(round(time.time() * 1000))
    print(Fore.BLUE + f"Search took {millisend-millisstart}ms")
    return best_answer


async def __search_method1(texts, answers, reverse):
    """
    Returns the answer with the maximum/minimum number of exact occurrences in the texts.
    :param texts: List of text to analyze
    :param answers: List of answers
    :param reverse: True if the best answer occurs the least, False otherwise
    :return: Answer that occurs the most/least in the texts, empty string if there is a tie
    """
    print("Running method 1...")
    counts = {answer.lower(): 0 for answer in answers}

    for text in texts:
        for answer in counts:
            counts[answer] += len(re.findall(f" {answer} ", text))

    print(counts)

    # If not all answers have count of 0 and the best value doesn't occur more than once and delta is less than 3 between the top 2 best values, return the best answer
    best_value = min(counts.values()) if reverse else max(counts.values())
    best_key = min(counts, key=counts.get) if reverse else max(
        counts, key=counts.get)
    counts2ndbest = counts.copy()
    counts2ndbest.pop(best_key, None)
    second_best_value = min(counts2ndbest.values()
                            ) if reverse else max(counts2ndbest.values())
    delta = (second_best_value -
             best_value) if reverse else (best_value-second_best_value)

    if not all(c == 0 for c in counts.values()) and list(counts.values()).count(best_value) == 1 and delta >= 3:
        best_answer = min(counts, key=counts.get) if reverse else max(
            counts, key=counts.get)
        return best_answer
    return ""


async def __search_method2(texts, answers, reverse):
    """
    Return the answer with the maximum/minimum number of keyword occurrences in the texts.
    :param texts: List of text to analyze
    :param answers: List of answers
    :param reverse: True if the best answer occurs the least, False otherwise
    :return: Answer whose keywords occur most/least in the texts with a difference of at least 3 with the second best one
    """
    print("Running method 2...")
    counts = {answer: {keyword: 0 for keyword in search.find_keywords(
        answer)} for answer in answers}

    for text in texts:
        for keyword_counts in counts.values():
            for keyword in keyword_counts:
                keyword_counts[keyword] += len(
                    re.findall(f" {keyword} ", text))

    counts_sum = {answer: sum(keyword_counts.values())
                  for answer, keyword_counts in counts.items()}
    print(counts_sum)
    best_value = min(counts_sum.values()) if reverse else max(
        counts_sum.values())
    best_key = min(counts_sum, key=counts_sum.get) if reverse else max(
        counts_sum, key=counts_sum.get)
    counts_sum_2nd_best = counts_sum.copy()
    counts_sum_2nd_best.pop(best_key, None)

    second_best_value = min(counts_sum_2nd_best.values()
                            ) if reverse else max(counts_sum_2nd_best.values())

    delta = (second_best_value -
             best_value) if reverse else (best_value-second_best_value)

    second_best_key = min(counts_sum_2nd_best, key=counts_sum_2nd_best.get) if reverse else max(
        counts_sum_2nd_best, key=counts_sum_2nd_best.get)
    if not all(c == 0 for c in counts_sum.values()) and list(counts_sum.values()).count(best_value) == 1 and delta >= 2:
        return min(counts_sum, key=counts_sum.get) if reverse else max(counts_sum, key=counts_sum.get)
    return ""


async def __search_method3(question_keywords, question_key_nouns, answers, reverse):
    """
    Returns the answer with the maximum number of occurrences of the question keywords in its searches.
    :param question_keywords: Keywords of the question
    :param question_key_nouns: Key nouns of the question
    :param answers: List of answers
    :param reverse: True if the best answer occurs the least, False otherwise
    :return: Answer whose search results contain the most keywords of the question
    """
    print("Running method 3...")
    search_results = await search.multiple_search(answers, 4)
    print("Search processed")
    answer_lengths = list(map(len, search_results))
    search_results = itertools.chain.from_iterable(search_results)

    texts = [x.translate(punctuation_to_none) for x in await search.get_clean_texts(search_results)]
    print("URLs fetched")
    answer_text_map = {}
    for idx, length in enumerate(answer_lengths):
        answer_text_map[answers[idx]] = texts[0:length]
        del texts[0:length]

    keyword_scores = {answer: 0 for answer in answers}
    noun_scores = {answer: 0 for answer in answers}

    # Create a dictionary of word to type of score so we avoid searching for the same thing twice in the same page
    word_score_map = defaultdict(list)
    for word in question_keywords:
        word_score_map[word].append("KW")
    for word in question_key_nouns:
        word_score_map[word].append("KN")

    answer_noun_scores_map = {}
    for answer, texts in answer_text_map.items():
        keyword_score = 0
        noun_score = 0
        noun_score_map = defaultdict(int)

        for text in texts:
            for keyword, score_types in word_score_map.items():
                score = len(re.findall(f" {keyword} ", text))
                if "KW" in score_types:
                    keyword_score += score
                if "KN" in score_types:
                    noun_score += score
                    noun_score_map[keyword] += score

        keyword_scores[answer] = keyword_score
        noun_scores[answer] = noun_score
        answer_noun_scores_map[answer] = noun_score_map

    # print()
    # print("\n".join([f"{answer}: {dict(scores)}" for answer,
        # scores in answer_noun_scores_map.items()]))

    print(f"Keyword scores: {keyword_scores}")
    print(f"Noun scores: {noun_scores}")
    best_noun_value = min(
        noun_scores.values()) if reverse else max(noun_scores.values())
    if set(noun_scores.values()) != {0} and list(noun_scores.values()).count(best_noun_value) == 1:
        return min(noun_scores, key=noun_scores.get) if reverse else max(noun_scores, key=noun_scores.get)
    if set(keyword_scores.values()) != {0}:
        return min(keyword_scores, key=keyword_scores.get) if reverse else max(keyword_scores, key=keyword_scores.get)
    return ""
