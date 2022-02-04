import json
import os
import datetime

INDEX = None

def intersectTwoLists(list_1, list_2):
    """
    Returns intersection of two lists.
    """
    result = []
    for idx in list_1:
        if idx in list_2:
            result.append(idx)
    return result

def conjuct(posting_lists):
    """
    Returns conjuction of lists.
    """
    # sorted_idx structure: [ [list_a_idx, list_a_length], [list_b_idx, list_b_length],...]
    sorted_idx = sorted([[id, len(posting_lists[id])] for id in range(len(posting_lists))], key=lambda x: x[1])

    result = intersectTwoLists(posting_lists[sorted_idx[0][0]],posting_lists[sorted_idx[1][0]])
    for idx in sorted_idx[2:]:
        result = intersectTwoLists(result, posting_lists[idx[0]])
    return result

def mergeTwoLists(list_1,list_2):
    """
    Merges two lists in ascending order.
    """
    # if one the lists is empty, just return the other list.
    if list_1 == []:
        return list_2
    if list_2 == []:
        return list_1

    result = []
    idx1=0
    idx2=0
    while idx1 < len(list_1) and idx2 < len(list_2):
        # while there are elements in both of the lists, do:
        if list_1[idx1] < list_2[idx2]:
            # if element in the first list is smaller than the element in the second list
            if  list_1[idx1]not in result:
                # and element in the second list is not in the result list
                # add it to the result list.
                result.append(list_1[idx1])
            # move to the next element of first list
            idx1 += 1
        elif list_1[idx1] >= list_2[idx2]:
            if list_2[idx2] not in result:
                result.append(list_2[idx2])
            idx2 += 1
    # one of the lists consumed, find out which one and append other list to the result.
    if idx1 == len(list_1) :
        if list_2[idx2] == result[-1]: ## to handle possible duplicate values
            idx2 +=1
        result.extend(list_2[idx2:])
    if idx2 == len(list_2) :
        if list_1[idx1] == result[-1]:## to handle possible duplicate values
            idx1 +=1
        result.extend(list_1[idx1:])
    return result


def disjunct(posting_lists):
    """
    Merges all posting lists.
    """
    result = posting_lists[0]
    for posting_list in posting_lists[1:]:
        result = mergeTwoLists(result,posting_list)
    return result

def negate(posting_lists_of_not,result):
    """
    removes the "not" terms from the result
    """
    for posting_list_of_not in posting_lists_of_not:
        for idx in posting_list_of_not:
            if idx in result:
                result.remove(idx)
    return result

def tokenizeQuery(terms):
    """
    Reads the input query and decides whether a term has not in front of it.
    """
    posting_lists = []
    posting_lists_of_not = []

    ## special part for first term
    posting_list = INDEX.get(terms[0])
    if posting_list != None:
        posting_lists.append(posting_list)
    else:
        posting_lists.append([])

    ### for rest of the terms, append to posting lists or posting_lists_of_not
    for i in range(1, len(terms)): # do not process or and not terms in query
        if terms[i] in ["or", "not", "and"]:
            continue
        posting_list = INDEX.get(terms[i])
        if terms[i - 1] == "not": # if prev terms is "not", add this posting list to posting_lists_of_not
            if posting_list != None:
                posting_lists_of_not.append(posting_list)
            else:# if word couldn't found, add an empty list
                posting_lists_of_not.append([])
        else:# if prev terms is "and" or "or", add this posting list to posting_lists
            if posting_list != None:
                posting_lists.append(posting_list)
            else:# if word couldn't found, add an empty list
                posting_lists.append([])
    return posting_lists, posting_lists_of_not

def search(terms, query_type):
    """
    Decides the type of the query and calls corresponding functions.
    """
    posting_lists, posting_lists_of_not = tokenizeQuery(terms)
    result = []    
    ### posting list merging for different types of queries
    if query_type == "conjunction": ### ANDs
        result = conjuct(posting_lists)

    if query_type == "disjunction": ### ORs
        result = disjunct(posting_lists)

    if query_type == "conjunction-and-negation": ### ANDs and NOTs
        result = conjuct(posting_lists)
        result = negate(posting_lists_of_not,result)

    if query_type == "disjunction-and-negation": ### ORS and NOTs
        result = disjunct(posting_lists)
        result = negate(posting_lists_of_not,result)

    if query_type == "one-word": ### only one word in search query
        posting_list = INDEX.get(terms[0])
        result = posting_list if posting_list is not None else []
    #print(result)
    return result

if __name__ == "__main__":
    # first load index_file to memory
    index_file = open('./myindex_unique.json',)
    INDEX = json.load(index_file)
    # add timestamp to the name of the output file
    file_name = "result_" + str(datetime.datetime.now()) +".json"
    f = open(file_name, "a")
    f.write("[")

    while True:
    # wait input from user continously
        terms = []
        query = input("\x1b[1;37;44m What is your search query? \x1b[1;37;41m(Press q for quit.)\x1b[0m ").lower()
        if query == "q":
            # if user typed 'q', close the program.
            f.close()
            with open(file_name, 'rb+') as filehandle:
                # deletes the final ", " part from the result file.
                filehandle.seek(-2, os.SEEK_END)
                filehandle.truncate()
            f = open(file_name, "a")
            f.write("]\n")
            f.close()
            print("Now you can see all the contents.")
            break
        else:
            # split the input to words and decide type of it.
            terms = query.split()
            result = {}
            if "not" not in terms:
                # if there is no "not" in input, look for "and" and "or"
                if "and" in terms:  # conjunction
                    result[query] = search(terms, query_type="conjunction")
                elif "or" in terms:  # disjunction
                    result[query] = search(terms, query_type="disjunction")
                else:
                    # if there is no "and" or "or", there must be only one word in the query
                    result[query] = search(terms, query_type="one-word")
            else:
                if "and" in terms:  # conjunction and negation
                    result[query] = search(terms, query_type="conjunction-and-negation")
                else:  # disjunction and negation
                    result[query] = search(terms, query_type="disjunction-and-negation")
            json.dump(result,f)
            f.write(", ")
            print("Result is saved to",file_name,"file. You can see it after closing the program.")
    
