import json
from bs4 import BeautifulSoup
import os

def JsonToDict(filePath):
    f = open(filePath, "r")
    l = f.read()
    f.close()
    return json.loads(l)

#input 5/54 for example
def getTextFromFilename(fileName):
    testFile = "WEBPAGES_RAW/" + fileName
    testToken = "metrowerks"
    f = open(testFile, "rb")
    fileString = f.read().decode("utf-8")
    soup = BeautifulSoup(fileString, 'html.parser')
    return soup.get_text()

def createSummaryText(tokenIndex, text):
    minIndex = max(0, tokenIndex-50)
    maxIndex = min(tokenIndex+50, len(text)-1)
  
    result = ""

    if minIndex != 0:
        result += "..."
        
    result += text[minIndex:maxIndex].replace("\n", " ")

    if maxIndex != len(text)-1:
        result += "..."
    
    s = "a\nb\nc\nd\n"
    result = str.join("", result.splitlines())
    result = ' '.join(result.split())
    return result

def getSummaryTextForToken(token, fileName):
    text = getTextFromFilename(fileName)
    
    index = text.lower().find(token)
    if index != -1:
        return createSummaryText(index, text)
    else:
        return "No summary available"

def getSortedPostingList(token, maxresults):
    try:
        postings = index[token]
    except KeyError as e: 
        return None
    else:
        sortedPostings = sorted(index[token].keys(), key = lambda x: index[token][x], reverse = True)
        maxRange = min(maxresults, len(sortedPostings)) # CHANGED, ranges aren't iterated inclusively (don't need -1)
        queryResults = []
        for i in range(0, maxRange):
            file = sortedPostings[i]
            fileUrl = Files[file]
            queryResults.append((fileUrl, getSummaryTextForToken(token, file)))
        return queryResults

index = JsonToDict("index.json")
Files = JsonToDict("WEBPAGES_RAW\\bookkeeping.json")
print(str(os.path.getsize("index.json") * 0.001) + "KB")
