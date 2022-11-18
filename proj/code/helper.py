import string
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()


def find_pos_tag(token):
    '''
    find pos_tag of the token
    '''
    pos_tag_list = wn.synsets(token)
    if len(pos_tag_list):
        return wn.synsets(token)[0].pos()
    else:
        return False


def lemmatize_token(token):
    '''
    lemmatize the token
    '''
    pos_tag = find_pos_tag(token)
    if find_pos_tag(token):
        lemmatized_token = lemmatizer.lemmatize(
            token, pos_tag)
        return lemmatized_token
    else:
        lemmatized_token = lemmatizer.lemmatize(
            token)
        return lemmatized_token


def add_key_to_term_dict(term_dict, term, docID, pos_idx):
    '''
    add a term to term_dict
    '''
    # token isn't in term_dict
    if term not in term_dict.keys():
        term_dict[term] = {}
        term_dict[term][docID] = []
        term_dict[term][docID].append(
            pos_idx)
        return 1
    # case the token is already in term_dict
    elif term in term_dict.keys():
        if docID in term_dict[term].keys():
            term_dict[term][docID].append(
                pos_idx)
        else:
            term_dict[term][docID] = []
            term_dict[term][docID].append(
                pos_idx
            )


def add_punctuation_to_term_dict(term_dict, punc, docID, pos_idx):
    '''
    add a punctuation to term_dict
    '''
    # the punctuation isn't in term_dict
    if punc not in term_dict.keys():
        term_dict[punc] = {}
        term_dict[punc][docID] = []
        term_dict[punc][docID].append(
            pos_idx)

    # case the token is already in term_dict
    elif punc in term_dict.keys():
        if docID in term_dict[punc].keys():
            term_dict[punc][docID].append(
                pos_idx)
        else:
            term_dict[punc][docID] = []
            term_dict[punc][docID].append(
                pos_idx
            )


# modify "phrase phrase" to (phrase + phrase)


def modify_phrase(query):
    modified_query = list(query)
    quotation_mark_count = 0
    while '"' in modified_query:
        quotation_mark_idx = modified_query.index("\"")
        # increase quotation mark count by 1
        quotation_mark_count += 1
        # quotation mark appears the first time
        # change to ( and add +1
        if quotation_mark_count % 2 != 0:
            modified_query[quotation_mark_idx] = "("
            first_space_idx = modified_query[quotation_mark_idx:].index(' ')
            adjusted_first_space_idx = quotation_mark_idx + first_space_idx
            modified_query[adjusted_first_space_idx] = " +1 "
            # look for the next word in the phrase
            # in case there're 2 more words in a phrase
            # find index of the next space
            try:
                modified_query[adjusted_first_space_idx:].index(' ')
                next_space_idx = modified_query[adjusted_first_space_idx:].index(
                    ' ')
                # adjust so that it's the index from quotation mark
                adjusted_next_space_idx = adjusted_first_space_idx + next_space_idx
                # find the index of the second quotation mark
                second_quotation_mark_idx = modified_query.index('"')
                # for all space before the secord quotation marks
                # replace space with " +1 "
                while adjusted_next_space_idx < second_quotation_mark_idx:
                    modified_query[adjusted_next_space_idx] = " +1 "
                    try:
                        next_space_idx = modified_query[adjusted_next_space_idx:].index(
                            ' ')
                        adjusted_next_space_idx = adjusted_next_space_idx + next_space_idx
                    except:
                        break
            except:
                pass
        else:
            modified_query[quotation_mark_idx] = ")"
            # reset quotation count
            quotation_mark_count = 0
    return ''.join(modified_query)


def is_term(elem):
    if elem.find("+") != -1 or elem.find("/") != -1 or elem.find("&") != -1 or elem.find("|") != -1:
        return False
    else:
        return True


# print formatted output
def print_formatted_output(ans_lst):
    formatted_output_lst = []
    res_lst = ans_lst[0]
    for res in res_lst:
        formatted_output_lst.append(int(res[0]))
    for elem in sorted(set(formatted_output_lst)):
        print(elem)


# To check for ) in a term


def find_close_bracket(term):
    if term.find(")") != -1:
        return True
    else:
        return False

# get rid of bracket in case
# term starts or end with ()


def get_rid_of_bracket(term):
    # having ( at index 0 of term
    if term.find("(") == 0:
        modified_term = term[1:]
        return modified_term
    # having ( at last index of term
    elif term.find(")") == len(term) - 1:
        modified_term = term[0:len(term) - 1]
        return modified_term

# query processing for numerical connector +1 or phrase
# the first search term must precede the secord term by n terms


def process_plus_one(term_dict, term_1, term_2, n=1):
    ans = []
    # check whether term 1 is a string or list:
    if isinstance(term_1, str) and isinstance(term_2, str):
        # find how many docID contains term_1 and term_2
        if term_1 in term_dict.keys() and term_2 in term_dict.keys():
            docID_term_1 = set(term_dict[term_1].keys())
            docID_term_2 = set(term_dict[term_2].keys())
            intersect_docID = docID_term_1.intersection(docID_term_2)
            for docID in intersect_docID:
                lst = []
                term_1_pos_lst = term_dict[term_1][docID]
                term_2_pos_lst = term_dict[term_2][docID]
                for term_1_pos in term_1_pos_lst:
                    for term_2_pos in term_2_pos_lst:
                        if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                            lst.append(term_2_pos)
                        elif term_2_pos > term_1_pos:
                            break
                    for term_2_pos in lst:
                        if term_2_pos - term_1_pos < 0 or term_2_pos - term_1_pos > n:
                            lst.remove(term_2_pos)
                    for term_2_pos in lst:
                        ans.append([docID, [term_1_pos, term_2_pos]])
            return ans
    # case term_1 is a list of positional index
    else:
        res_lst = term_1
        for res in res_lst:
            docID = res[0]
            # if term_2 is in the same docID with res
            # check if it's preceded by n by res
            if term_2 in term_dict.keys():
                if docID in term_dict[term_2].keys():
                    term_1_pos_lst = res[1]
                    term_2_pos_lst = term_dict[term_2][docID]
                    for term_1_pos in term_1_pos_lst:
                        for term_2_pos in term_2_pos_lst:
                            if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                                res[1].append(term_2_pos)
                                ans.append(res[1])
                            elif term_2_pos > term_1_pos:
                                break
        return ans


# process "phrase"

def process_phrase(term_dict, query):
    query_split = query.split(" ")
    # each +1 in query split is basically phrase
    # so find it
    plus_one_count = 0
    while "+1" in query_split:
        plus_one_count += 1
        # first time to detect +1 in the list means
        # the preceded element in the list having (
        if plus_one_count == 1:
            plus_one_idx = query_split.index("+1")
            # preceded_term with bracket
            preceded_term = query_split[plus_one_idx - 1]
            # get rid of (
            mod_preceded_term = get_rid_of_bracket(preceded_term)
            followed_term = query_split[plus_one_idx + 1]
            # determine the length of phrase by
            # check for clost bracket
            if followed_term[-1] == ")":
                # get rid of bracket and process phrase
                mod_followed_term = get_rid_of_bracket(followed_term)
                tmp = process_plus_one(
                    term_dict, mod_preceded_term, mod_followed_term, 1)
                # after process +1, remove processed elements
                # and replace with the list
                query_split.pop(plus_one_idx)
                query_split.remove(preceded_term)
                followed_term_idx = query_split.index(followed_term)
                query_split[followed_term_idx] = tmp
                # reset plus_one_count to 0
                plus_one_count = 0
                continue
            # case there're more than 2 terms in a phrase
            else:
                tmp = process_plus_one(
                    term_dict, mod_preceded_term, followed_term, 1)
                # after process +1, remove processed elements
                # and replace with the list
                query_split.pop(plus_one_idx)
                query_split.remove(preceded_term)
                followed_term_idx = query_split.index(followed_term)
                query_split[followed_term_idx] = tmp
                continue
        # case not at the beginning of the phrase
        else:
            # find index of +1
            plus_one_idx = query_split.index("+1")
            preceded_term = query_split[plus_one_idx - 1]
            followed_term = query_split[plus_one_idx + 1]
            if find_close_bracket(followed_term):
                mod_followed_term = get_rid_of_bracket(followed_term)
                tmp = process_plus_one(
                    term_dict, preceded_term, mod_followed_term, 1)
                # after process +1, remove processed elements
                # and replace with the list
                query_split.pop(plus_one_idx)
                query_split.remove(preceded_term)
                followed_term_idx = query_split.index(followed_term)
                query_split[followed_term_idx] = tmp
                # reset plus_one_count to 0
                plus_one_count = 0
                continue
            else:
                tmp = process_plus_one(
                    term_dict, preceded_term, followed_term, 1)
                # after process +1, remove processed elements
                # and replace with the list
                query_split.pop(plus_one_idx)
                query_split.remove(preceded_term)
                followed_term_idx = query_split.index(followed_term)
                query_split[followed_term_idx] = tmp
                continue
    return query_split

# change all or operation to |


def modify_or(query):
    query_split = query.split(" ")
    # for any adjacent terms without operation between
    idx = 0
    for idx in range(0, len(query_split) - 1):
        elem = query_split[idx]
        next_elem = query_split[idx + 1]
        if is_term(elem) and is_term(next_elem):
            query_split.insert(idx + 1, '|')
    return ' '.join(query_split)

# process or


def process_or(term_dict, query):
    res_lst = query
    # each adjacent terms or list in query split
    # is basically or operation
    # if isinstance(query, list):
    or_count = 0
    while "|" in query:
        # find idx of | in query_split
        or_idx = query.index("|")
        # preceded_term
        preceded_term = query[or_idx - 1]
        # followed_term
        followed_term = query[or_idx + 1]
        if isinstance(preceded_term, str) and isinstance(followed_term, str):
            res_lst = []
            if preceded_term in term_dict.keys():
                for docID in term_dict[preceded_term]:
                    pos_idx_lst = term_dict[preceded_term][docID]
                    res = [docID]
                    res.append([idx for idx in pos_idx_lst])
                    res_lst.append(res)
            if followed_term in term_dict.keys():
                for docID in term_dict[followed_term]:
                    pos_idx_lst = term_dict[followed_term][docID]
                    res = [docID]
                    res.append([idx for idx in pos_idx_lst])
                    res_lst.append(res)
            # after process |, remove processed elements
            # and replace with the list
            query.pop(or_idx)
            query.remove(preceded_term)
            followed_term_idx = query.index(followed_term)
            query[followed_term_idx] = res_lst
            continue
        elif isinstance(preceded_term, list) and isinstance(followed_term, str):
            # case term_1 is a list of positional index
            res_lst = preceded_term
            if followed_term in term_dict.keys():
                for docID in term_dict[followed_term]:
                    pos_idx_lst = term_dict[followed_term][docID]
                    res = [docID]
                    res.append([idx for idx in pos_idx_lst])
                    res_lst.append(res)
                    continue
        elif isinstance(preceded_term, str) and isinstance(followed_term, list):
            # case term_1 is a list of positional index
            res_lst = followed_term
            if preceded_term in term_dict.keys():
                for docID in term_dict[preceded_term]:
                    pos_idx_lst = term_dict[preceded_term][docID]
                    res = [docID]
                    res.append([idx for idx in pos_idx_lst])
                    res_lst.append(res)
            # after process |, remove processed elements
            # and replace with the list
            query.pop(or_idx)
            query.remove(preceded_term)
            followed_term_idx = query.index(followed_term)
            query[followed_term_idx] = res_lst
            continue
        # case both preceded and followed terms are list
        else:
            res_lst = preceded_term
            for res in followed_term:
                res_lst.append(res)
            # after process |, remove processed elements
            # and replace with the list
            query.pop(or_idx)
            query.remove(preceded_term)
            followed_term_idx = query.index(followed_term)
            query[followed_term_idx] = res_lst
            continue
    return query


# query processing for numerical connector +n
# the first search term must precede the secord term by n terms


def process_plus_n(term_dict, query):
    ans_lst = query
    idx = 1
    while idx <= len(query) - 2:
        elem = query[idx]
        if elem.find("+") != -1 and elem.isnumeric() != -1:
            ans = []
            term_1 = query[idx - 1]
            term_2 = query[idx + 1]
            n = int(elem[1:])
            # case both term_1 and term_2 are string
            if isinstance(term_1, str) and isinstance(term_2, str):
                # find how many docID contains term_1 and term_2
                if term_1 in term_dict.keys() and term_2 in term_dict.keys():
                    docID_term_1 = set(term_dict[term_1].keys())
                    docID_term_2 = set(term_dict[term_2].keys())
                    intersect_docID = docID_term_1.intersection(
                        docID_term_2)
                    for docID in intersect_docID:
                        lst = []
                        term_1_pos_lst = term_dict[term_1][docID]
                        term_2_pos_lst = term_dict[term_2][docID]
                        for term_1_pos in term_1_pos_lst:
                            for term_2_pos in term_2_pos_lst:
                                if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                                    lst.append(term_2_pos)
                                elif term_2_pos > term_1_pos:
                                    break
                            for term_2_pos in lst:
                                if term_2_pos - term_1_pos < 0 or term_2_pos - term_1_pos > n:
                                    lst.remove(term_2_pos)
                            for term_2_pos in lst:
                                ans.append([docID, term_1_pos, term_2_pos])
                    # after process |, remove processed elements
                    # and replace with the list
                    ans_lst.pop(idx)
                    ans_lst.remove(term_1)
                    term_2_idx = ans_lst.index(term_2)
                    ans_lst[term_2_idx] = ans
                    idx = 1
                    print(ans_lst)
                    continue
            # case term_1 is a list and term_2 is a string
            elif isinstance(term_1, list) and isinstance(term_2, str):
                res_lst_1 = term_1
                for res_1 in res_lst_1:
                    docID = res_1[0]
                    # if term_2 is in the same docID with res
                    # check if it's preceded by n by res
                    if term_2 in term_dict.keys():
                        if docID in term_dict[term_2].keys():
                            lst = []
                            term_1_pos_lst = res_1[1]
                            term_2_pos_lst = term_dict[term_2][docID]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                                        lst.append(term_2_pos)
                                for term_2_pos in lst:
                                    if term_2_pos - term_1_pos < 0 or term_2_pos - term_1_pos > n:
                                        lst.remove(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                for term_2_pos in lst:
                                    ans.append(
                                        [docID, [term_1_pos, term_2_pos]])
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                print(ans)
                continue
            elif isinstance(term_1, str) and isinstance(term_2, list):
                res_lst_1 = term_2
                for res_1 in res_lst_1:
                    docID = res_1[0]
                    # if term_2 is in the same docID with res
                    # check if it's preceded by n by res
                    if term_1 in term_dict.keys():
                        if docID in term_dict[term_1].keys():
                            lst = []
                            term_1_pos_lst = term_dict[term_1][docID]
                            term_2_pos_lst = res_1[1]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                                        lst.append(term_2_pos)
                                for term_2_pos in lst:
                                    if term_2_pos - term_1_pos < 0 or term_2_pos - term_1_pos > n:
                                        lst.remove(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                for term_2_pos in lst:
                                    ans.append(
                                        [docID, [term_1_pos, term_2_pos]])
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                print(ans)
                continue
            elif isinstance(term_1, list) and isinstance(term_2, list):
                res_lst_1 = term_1
                res_lst_2 = term_2
                for res_1 in res_lst_1:
                    docID_1 = res_1[0]
                    for res_2 in res_lst_2:
                        docID_2 = res_2[0]
                        if docID_1 == docID_2:
                            lst = []
                            term_1_pos_lst = res_1[1]
                            term_2_pos_lst = res_2[1]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if term_2_pos - term_1_pos > 0 and term_2_pos - term_1_pos <= n:
                                        lst.append(term_2_pos)
                                for term_2_pos in lst:
                                    if term_2_pos - term_1_pos < 0 or term_2_pos - term_1_pos > n:
                                        lst.remove(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                for term_2_pos in lst:
                                    res = [docID_1, [term_1_pos, term_2_pos]]
                                    if res not in ans:
                                        ans.append(res)
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                print(ans)
                continue
        idx += 2
    return ans_lst

# query processing for numerical connector /n
# the search term must appear within n terms of each other


def process_slash_n(term_dict, query):
    ans_lst = query
    idx = 1
    while idx <= len(query) - 2:
        elem = query[idx]
        if elem.find("/") != -1 and elem.isnumeric() != -1:
            ans = []
            term_1 = query[idx - 1]
            term_2 = query[idx + 1]
            n = int(elem[1:])
            # case both term_1 and term_2 are string
            if isinstance(term_1, str) and isinstance(term_2, str):
                # find how many docID contains term_1 and term_2
                if term_1 in term_dict.keys() and term_2 in term_dict.keys():
                    docID_term_1 = set(term_dict[term_1].keys())
                    docID_term_2 = set(term_dict[term_2].keys())
                    intersect_docID = docID_term_1.intersection(
                        docID_term_2)
                    for docID in intersect_docID:
                        lst = []
                        term_1_pos_lst = term_dict[term_1][docID]
                        term_2_pos_lst = term_dict[term_2][docID]
                        for term_1_pos in term_1_pos_lst:
                            for term_2_pos in term_2_pos_lst:
                                if abs(term_2_pos - term_1_pos) <= n:
                                    lst.append(term_2_pos)
                                elif term_2_pos > term_1_pos:
                                    break
                            while lst != [] and abs(lst[0] - term_1_pos) > n:
                                lst.remove(lst[0])
                            for term_2_pos in lst:
                                res = [docID, [term_1_pos, term_2_pos]]
                                if res not in ans:
                                    ans.append(res)
                    # after process |, remove processed elements
                    # and replace with the list
                    ans_lst.pop(idx)
                    ans_lst.remove(term_1)
                    term_2_idx = ans_lst.index(term_2)
                    ans_lst[term_2_idx] = ans
                    idx = 1
                    continue
            # case term_1 is a list and term_2 is a string
            elif isinstance(term_1, list) and isinstance(term_2, str):
                res_lst_1 = term_1
                for res_1 in res_lst_1:
                    docID = res_1[0]
                    # if term_2 is in the same docID with res
                    # check if it's preceded by n by res
                    if term_2 in term_dict.keys():
                        if docID in term_dict[term_2].keys():
                            lst = []
                            term_1_pos_lst = res_1[1]
                            term_2_pos_lst = term_dict[term_2][docID]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if abs(term_2_pos - term_1_pos) <= n:
                                        lst.append(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                while lst != [] and abs(lst[0] - term_1_pos) > n:
                                    lst.remove(lst[0])
                                for term_2_pos in lst:
                                    res = [docID, [term_1_pos, term_2_pos]]
                                    if res not in ans:
                                        ans.append(res)
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                continue
            elif isinstance(term_1, str) and isinstance(term_2, list):
                res_lst_1 = term_2
                for res_1 in res_lst_1:
                    docID = res_1[0]
                    # if term_2 is in the same docID with res
                    # check if it's preceded by n by res
                    if term_1 in term_dict.keys():
                        if docID in term_dict[term_1].keys():
                            lst = []
                            term_1_pos_lst = term_dict[term_1][docID]
                            term_2_pos_lst = res_1[1]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if abs(term_1_pos - term_2_pos) <= n:
                                        lst.append(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                while lst != [] and abs(lst[0] - term_1_pos) > n:
                                    lst.remove(lst[0])
                                for term_2_pos in lst:
                                    res = [docID, [term_1_pos, term_2_pos]]
                                    if res not in ans:
                                        ans.append(res)
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                continue
            elif isinstance(term_1, list) and isinstance(term_2, list):
                res_lst_1 = term_1
                res_lst_2 = term_2
                for res_1 in res_lst_1:
                    docID_1 = res_1[0]
                    for res_2 in res_lst_2:
                        docID_2 = res_2[0]
                        if docID_1 == docID_2:
                            lst = []
                            term_1_pos_lst = res_1[1]
                            term_2_pos_lst = res_2[1]
                            for term_1_pos in term_1_pos_lst:
                                for term_2_pos in term_2_pos_lst:
                                    if abs(term_2_pos - term_1_pos) <= n:
                                        lst.append(term_2_pos)
                                    elif term_2_pos > term_1_pos:
                                        break
                                while lst != [] and abs(lst[0] - term_1_pos) > n:
                                    lst.remove(lst[0])
                                for term_2_pos in lst:
                                    res = [docID_1, [term_1_pos, term_2_pos]]
                                    if res not in ans:
                                        ans.append(res)
                # after process |, remove processed elements
                # and replace with the list
                ans_lst.pop(idx)
                ans_lst.remove(term_1)
                term_2_idx = ans_lst.index(term_2)
                ans_lst[term_2_idx] = ans
                idx = 1
                continue
        idx += 2
    return ans_lst
