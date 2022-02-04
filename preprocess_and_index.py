import os
import string
import threading
import json

FILE_NAMES = [] # this list holds the names of the reuter files.
STOPWORDS = [] # this list holds the stopwords
RETURN_VALUES_OF_THREADS = {} # this dictionary holds the values returned from extractBody function which is executed parallelly by threads.


def getFileNames():
    """
    This function traverses reuters21578 folder and appends names of sgm files to global FILE_NAMES list.
    """
    for file in os.listdir("./reuters21578"):
        if file.endswith(".sgm"):
            FILE_NAMES.append(os.path.join("./reuters21578", file))


def getStopwords():
    """
    This function reads stopwords.txt and stores those stopwords in global STOPWORDS list.
    """
    f = open("./stopwords.txt", "r")
    for line in f.readlines():
        STOPWORDS.append(line.strip())
    f.close()


def invertArticle(ID, TEXT):
    """
    This function returns an inverted index of an article.
    It takes the ID and TEXT part of the article and creates the inverted index.
    Since term frequency does not matter, list is unique.
    Example return value: {"term_1": ID, "term_2": ID, "term_3": ID, "term_4": ID,..}
    """
    posting_list = {}
    for word in TEXT:
        if word == '':
            continue
        if word not in posting_list:
            posting_list[word] = ID
    return posting_list

def merge(postings):
    """
    This function merges the inverted indexes of articles from a file. 
    For every smg sile, this function is called at the end of the "preprocess()" function.
    Example return value: {"term_1": [ID1, ID2, ID999], "term_2": [ID1, ID54], "term_3": [ID1, ID2, ID45, ID876], ...}
    """
    big_posting = {} # this is the return value
    for posting in postings: # example postings content:  [{"term_1": ID1, "term_2": ID1, "term_3": ID1, ...}, {"term_1": ID2, "term_3": ID2, ...}, ..]
        for key, val in posting.items():
            if key not in big_posting: # if key was not in the list previously, create it
                big_posting[key] = [val]
            else: # if key is already in the list, append new id next to it.
                big_posting[key].append(val)
    return big_posting

def preprocess(file_name):
    """
    This function preprocess the reuters_xx.smg file.
    It reads the file article by article and stores the inverted index of each article in the "postings" variable.
    Then it calls the "merge()" function stores the returned value in global RETURN_VALUES_OF_THREADS variable.
    """
    with open(file_name, "rb") as f:
        contents = f.read().decode("latin-1") # read smg file in latin-1 encoding
        postings = []
        while len(contents) > 0: # read article by article
            article = contents[contents.find("<REUTERS"):contents.find("/REUTERS>")+9] # an article is surrounded with <REUTERS> tags.
            new_id_idx = article.find('NEWID=') # find location of NEWID in the article
            if new_id_idx > -1: # if found assign it to NEWID variable
                NEWID = int(article[new_id_idx+7:article.find('>')-1])
            else: # if not found, move on to next article
                contents = contents[contents.find("/REUTERS>") + 9:]
                continue
            title_idx = article.find("<TITLE>") # title is surrounded with <TITLE> tags. Find its location
            if title_idx > -1: # if found assign it to TITLE variable
                TITLE = article[title_idx+7:article.find("</TITLE>")]
            else: # if not found, assume its empty
                TITLE = ""
            body_idx = article.find("<BODY>") # body is surrounded with <BODY> tags. Find its location
            if body_idx > -1: # if found assign it to BODY variable
                BODY = article[body_idx+6:article.find("</BODY>")]
            else: # if not found, assume its empty
                BODY = ""

            # merge title and body of the article
            BODY = TITLE + " " + BODY

            # case-folding : lower every character in the article
            BODY = BODY.lower()

            # \n removal : remove newline characters from article
            BODY = BODY.replace("\n", " ")

            # stopword removal : remove stopwords from article
            for stopword in STOPWORDS:
                BODY = BODY.replace(' '+stopword+' ', ' ')

            # punctuation removal : remove punctuations by cponverting them to space characters.
            BODY = BODY.translate(BODY.maketrans(
                '', '', string.punctuation)).split(" ")

            postings.append(invertArticle(NEWID, BODY)) # append inverted index to the "posting" variable.
            contents = contents[contents.find("/REUTERS>") + 9:] # move on to next article

    # store return value of this function in a global variable
    RETURN_VALUES_OF_THREADS[file_name] = merge(postings)


if __name__ == "__main__":
    """
    
    """
    getFileNames() # store filenames in the global variable
    getStopwords() # store stopwords in the global variable

    threads = []
    for file in FILE_NAMES:
        # create threads for preprocessing each file
        extract_body_thread = threading.Thread(target=preprocess, args=(file,))
        threads.append(extract_body_thread)
        extract_body_thread.start()

    for thread in threads:
        # wait for threas to finish
        thread.join()

    biggest_posting = {}

    for filename in sorted(RETURN_VALUES_OF_THREADS.keys()):
        # append inverted indexes starting from first file, so that final result can be sorted automatically.
        posting_list = RETURN_VALUES_OF_THREADS[filename]
        for key, val in posting_list.items():
            if key not in biggest_posting:
                biggest_posting[key] = val
            else:
                biggest_posting[key].extend(val)
    # write index to file in json format
    f = open("myindex_unique.json", "w")
    json.dump(biggest_posting, f)
    