from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from interruptingcow import timeout

import math
import lxml
from lxml import etree
import os
from urllib.parse import urljoin, urlparse
import re
import json


def log_frequency_weight(tf):
    if tf > 0:
        return 1 + math.log(tf, 10)
    else:
        return 0

'''
df: document frequency of a term
n: total number of documents in the corpus
'''
def inverse_document_frequency(df, n):
    return math.log(n/df, 10)

'''
Given the term frequency, document frequency, and N, computes tf-idf score
'''
def tf_idf_weight(tf, df, n):
    return log_frequency_weight(tf) * inverse_document_frequency(df, n) 

def is_duplicate(url):
        # Determines if there are any repeating folder names in a full url path
        subdomain = re.split('/', url)
        subdomain = subdomain[2:]
        subdirectories = set()
        for sub in subdomain:
            if (sub not in subdirectories):
                subdirectories.add(sub)
            elif (sub in subdirectories):
                return True    
        return False
    
def query_param_too_long(url):
    if (url.find("?") != -1):
        url_string = str(url)
        url_string = url_string[url_string.find("?")+1:]
        urlqueryparams = url_string.split("&")
        for param in urlqueryparams:
            if (len(param[param.find("=")+1:]) >= 30):
                #print(url, param[param.find("=")+1:])
                return True
    return False

def is_valid(url):
    """
    Function returns True or False based on whether the url has to be fetched or not. This is a great place to
    filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
    in this method
    """

    # TO DO: Filter out crawler traps (e.g. the ICS calendar, dynamic URL’s, etc.) You will need to do some research online or
    # apply concepts regarding crawler traps covered in class.

    parsed = urlparse(url)
    if len(url) > 300:
        #print("Large len", url)
        return False
    if is_duplicate(url): # skip anything with duplicates in the path
        #print("Duplicate Blocked:", url)
        return False
    if (query_param_too_long(url)):# and (url.find("") != -1) and self.passable_search_url(url): # skip anything with a question mark, unless in "passable" list
        return False
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
               and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                + "|thmx|mso|arff|rtf|jar|csv" \
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        return False

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def DictToJson(dict, fileName):
    with open(fileName, 'w') as json_file:
        json.dump(dict, json_file)

if (__name__ == "__main__"): 
    all_tokens = set()
    term_freqs = {}
 
    flag = 0
 
    Files = JsonToDict("WEBPAGES_RAW/bookkeeping.json")
    
    skippedFiles = []

    for rawFileName in Files:
        flag += 1
        
        file = Files[rawFileName] # URL NAME
        filePath = "WEBPAGES_RAW/" + rawFileName #.replace('/', "\\") # Built Path, location on memory
        
        valid = is_valid("http://" + file) or is_valid("https://" + file)
        
        if valid:
            try:
                with timeout(5, RuntimeError):
                    f = open(filePath, "rb")
                    fileString = f.read().decode("utf-8")
                       
                    soup = BeautifulSoup(fileString, 'html.parser')
                    Text = soup.get_text()
                    
                    AllTokens = word_tokenize(Text)
                    
                    stopWords = set(stopwords.words('english'))
                    wordsFiltered = []
                    for token in AllTokens:
                        if (token not in stopWords) and isEnglish(token) and (token.isalpha()) and (len(token) >= 3):
                            token = token.lower()
                            all_tokens.add(token)  
                            if token not in term_freqs.keys(): 
                                term_freqs[token] = {}
                                term_freqs[token][rawFileName] = 1
                            else: 
                                if rawFileName in term_freqs[token].keys():
                                    term_freqs[token][rawFileName] += 1  
                                else:
                                    term_freqs[token][rawFileName] = 1

            except RuntimeError:
                print(rawFileName, ('(' + str(flag) + ')'), "TOOK TOO DAMN fuckin LONG")
                skippedFiles.append(rawFileName)   

    print('----------------------------------------------------')
    index = {}
    for token in term_freqs.keys():
        index[token] = {}
        df = len(term_freqs[token].keys())
        for doc in term_freqs[token].keys():
            index[token][doc] = tf_idf_weight(term_freqs[token][doc], df, flag)
        
    for item in sorted(index.keys()):
       print(item, ":", index[item])
    
    DictToJson(term_freqs, "term_freqs.json")    
    DictToJson(index, "index.json")  
    DictToJson(skippedFiles, "index_skipped.json")
    
    data = JsonToDict("term_freqs.json")