from __future__ import division
from nltk.corpus import reuters
from nltk.corpus import stopwords
import re
import operator
#from os import listdir
from os.path import isfile, join
from math import log
import time

start_time = time.time()


trainset=[]
testset=[]
sw = stopwords.words('english')
swd={}

for w in sw:
    swd[w]=True
#Here, apart from the naive bayes classifier, everything is done by nltk

##2)Forming Prepare the CatNumDocs dictionary, where the number of documents in the training set for each
             ##category are stored
    ##also forming the training set and test set
    ##No need of reverse dictionary as getting the category from the fileid is straighforward
categoriesFilenameDict={}
CatNumDocs={}

cleanFiles = [f for f in reuters.fileids() if len(reuters.categories(fileids=f))==1]
testset = [f for f in cleanFiles if f[:5]=='test/']
trainset = [f for f in cleanFiles if f[:9]=='training/']
for cat in reuters.categories():
    li=[f for f in reuters.fileids(categories=cat) if f in trainset]
    liTe = [f for f in reuters.fileids(categories=cat) if f in testset]
    if len(li)>20 and len(liTe)>20:
        CatNumDocs[cat]=len(li)
        li.extend(liTe)
        categoriesFilenameDict[cat]=li

trainset = [ f for f in trainset if reuters.categories(fileids=f)[0] in categoriesFilenameDict]    
testset = [ f for f in testset if reuters.categories(fileids=f)[0] in categoriesFilenameDict]

    


###--------------------DEBUG STATEMENTS----------------------
#for f in trainset:
 #   print f , FilenameCategoriesDict[f] 

#print "Freedom\n"

#for f in testset:
 #   print f    
###--------------------DEBUG STATEMENTS----------------------
    
##3) Information Theoritic Mutual Information - Feature Selection - including only those words as features which have the highest
 ##mutual information for a category - selecting top x words for a category
##A)Create a dictionary with a word as the key and a dictionary as the value
 ## in the dictionary the category as key and number of documents in that category where it occurs as value

WordCatNumDocDict={}
numTopWords=500
N = len(trainset)

##B)Loop through the reuters dataset, to get the entire text from  each file in the training set

for fileName in trainset:
    string = reuters.raw(fileids=fileName)

##C) Parse the string to get individual words


    listWords = re.split(r'\W+',string)
    listWords = [w.lower() for w in listWords if w.isalpha() and len(w)>1 and  not swd.get(w.lower(),False)]
    #!!!!!!!!------Possible Improvement: Stemming--------------#
    
    cat = reuters.categories(fileids=fileName)[0]
    
##D) Update the dictionary
    for w in set(listWords):
        WordCatNumDocDict[w]=WordCatNumDocDict.get(w,{})
        WordCatNumDocDict[w][cat]=WordCatNumDocDict[w].get(cat,0)
        WordCatNumDocDict[w][cat]+=1



##E) Prepare a dictionary with key category and value as list of tuples of words with word strings  and
        #mutual information as the 2 elements of the tuple which will be the only ones considered as features
    ## and a list with all these word features
WordFeatures={}
WordList={}
for w in WordCatNumDocDict.keys():
    dic = WordCatNumDocDict[w]
    N1x=0
    for cat in dic.keys():
        N1x+=dic[cat] ## number of documents in the training set where the word occurs
    for cat in dic.keys():
        WordFeatures[cat]=WordFeatures.get(cat,[])
        Nx1=CatNumDocs[cat] ## number of documents in the training set of the particular category
        N11=dic[cat]
        N01=Nx1-N11 ## num documents of the category where the word does not occur in trainset
        N10=N1x-N11 ## num documents of other categories where the word occurs
        N00 = N - (N01+N10+N11)
        MI=(N11/N)*log((N*N11)/(N1x*N1x))/log(2)
        if N01!=0:
            MI-=(N01/N)*log((N*N01)/((N-N1x)*N1x))/log(2)
        if N10!=0:
            MI-=(N10/N)*log((N*N10)/((N-N1x)*N1x))/log(2)
        #if N00!=0:
         #   MI+=(N00/N)*log((N*N00)/((N-N1x)*(N-N1x)))/log(2)

        if len(WordFeatures[cat])<numTopWords:
            WordFeatures[cat].append((w,MI))
            if len(WordFeatures[cat])==numTopWords:
                WordFeatures[cat].sort(key=operator.itemgetter(1),reverse=True)                
        else:
            if WordFeatures[cat][numTopWords-1][1]<MI:
                WordFeatures[cat][numTopWords-1]= (w,MI)
            WordFeatures[cat].sort(key=operator.itemgetter(1),reverse=True)                


for cat in WordFeatures.keys():
    #print cat
    #print WordFeatures[cat]
    #print "\n"
    WordFeatures[cat]=dict(WordFeatures[cat])
    for w in WordFeatures[cat]:
         WordList[w]=True
    
##4)Create a) a dictionary with a category as the key and dictionary of words-occurences as values
          #b) a dictionary with a category as the key and the number of words in it as the value
CatWordDict={}
CatWordCountDict={}
#val = my_dict.get(key, mydefaultval)

##5)Loop through the training set, to get the entire text from  each file

for fileName in trainset:
    string = reuters.raw(fileids=fileName)

##6) Parse the string to get individual words

    cat = reuters.categories(fileids=fileName)[0]
    listWords = re.split(r'\W+',string)
    listWords = [w.lower() for w in listWords if w.isalpha() and len(w)>1 and not swd.get(w.lower(),False)
                 and WordFeatures[cat].get(w.lower(),-100000)!=-100000]
    #!!!!!!!!------Possible Improvement: Stemming--------------#


##7) Check if category exists in dictionary, if not, create an empty dictionary,
    #and put word count as zero
    #and then insert words into the category's dictionary in both cases and update the word count
    cat = reuters.categories(fileids=fileName)[0]
    if CatWordDict.get(cat, -1)==-1:
        CatWordDict[cat]={}
        CatWordCountDict[cat]=0
 ##Update the dictionary - 2 possible ways
    ##A) loop over the set of words and update dictionary with log value
        ##Complexity- n(set)*n(count operation) = O(n^2)
    ##B) loop over list and update count for each occurence
        #at the end, loop over set and replace count with log value
        ##Complexity- n(list)+n(set) = O(n)
        ##B is better and takes one second lesser time to prepare the index

    CatWordCountDict[cat]+=len(listWords)

    ##A)
    #for w in set(listWords):
     #   CatWordDict[cat][w] = CatWordDict[cat].get(w,0)
      #  CatWordDict[cat][w]+= listWords.count(w)           
    ##B)
    for w in listWords:
        CatWordDict[cat][w] = CatWordDict[cat].get(w,0)
        CatWordDict[cat][w]+= 1
        

##8) Get the vocabulary length
vocabLength=0            
for cat in CatWordDict.keys():
    length = len(CatWordDict[cat])
    print cat, length
    vocabLength+=length


####Congratulations! the Classifier is trained, now it is time to run the Multinomial Naive Bayes Classifier on the test dataset
print "The Classifier is trained and it took"
print time.time() - start_time, "seconds"
start_time = time.time()



liResults=[]
#9) Like in the training set,Loop through the test set, to get the entire text from  each file
for fileName in testset:
    minimumNegLogProb=1000000000
    minCategory=''
    string = reuters.raw(fileids=fileName)

##10) Similar step, parse the string to get individual words

    listWords = re.split(r'\W+',string)
    listWords = [w.lower() for w in listWords if w.isalpha() and len(w)>1 and not swd.get(w.lower(),False)
                 and WordList.get(w.lower(),False)]
    #!!!!!!!!------Possible Improvement: Stemming--------------#
    if fileName=='test/15024':
        print listWords
    
##11) Get the probability for each category,
    #can use any of the created dictionaries to wade through the categories
    for cat in  CatWordCountDict:
        ###--------------------DEBUG STATEMENTS----------------------
        #print cat , CatNumDocs[cat]/len(trainset)
        ###--------------------DEBUG STATEMENTS----------------------
        negLogProb=-log(CatNumDocs[cat]/len(trainset))
        wordDict = CatWordDict[cat]
        countCat = CatWordCountDict[cat]
        for w in listWords:
            countWordTrain=wordDict.get(w,0)
            ratio = (countWordTrain+1)/(countCat+vocabLength)
            negLogProb-=log(ratio)           
                         
        if minimumNegLogProb>negLogProb:
            minCategory=cat
            minimumNegLogProb=negLogProb

    liResults.append((fileName,minCategory,reuters.categories(fileids=fileName)[0]))

###--------------------DEBUG STATEMENTS----------------------
#for t in liResults:
 #   print t    
###--------------------DEBUG STATEMENTS----------------------
    
#12) Create a dictionary with category as the key and a list of 4 numbers as the value
 #These values are a) Number of docs in the category identified correctly a
                  #b) Number of docs identified incorrectly as in the category b
                  #c) Number of docs identified incorrectly as not in the category c
                  #d) Number of docs identified correctly as not in the category d
CatResultsDict = {}
for cat in CatWordCountDict:
    CatResultsDict[cat]=[0,0,0,0]
    for t in liResults:
        if cat==t[1]:
            if cat==t[2]:
                CatResultsDict[cat][0]+=1
            else:
                CatResultsDict[cat][1]+=1
        else:
            if cat==t[2]:
                CatResultsDict[cat][2]+=1
            else:
                CatResultsDict[cat][3]+=1

totPrec=0
totRec=0
A=0
B=0
C=0
D=0
for cat in CatResultsDict:
    a = CatResultsDict[cat][0]
    b = CatResultsDict[cat][1]
    c = CatResultsDict[cat][2]
    d = CatResultsDict[cat][3]
    totPrec+=a/(a+b)##Precision for this category
    totRec+=a/(a+c)##Recall for this category
    A+=a
    B+=b
    C+=c
    D+=d
###--------------------DEBUG STATEMENTS----------------------
    #print cat, a
    #print cat, b
    #print cat, c
    #print cat, d
    #print (a+b+c+d)==len(testset)
###--------------------DEBUG STATEMENTS----------------------
MacroPrec = totPrec/len(CatResultsDict)
MacroRec = totRec/len(CatResultsDict)
MacroF = (2*MacroPrec*MacroRec)/(MacroPrec+MacroRec)

MicroPrec = A/(A+B)
MicroRec = A/(A+C)
MicroF = (2*MicroPrec*MicroRec)/(MicroPrec+MicroRec)

print "Macro Precision=",MacroPrec
print "Macro Recall=",MacroRec
print "Macro F-measure=",MacroF

print "Micro Precision=",MicroPrec
print "Micro Recall=",MicroRec
print "Micro F-measure=",MicroF

    



numErrors = sum(t[1]!=t[2] for t in liResults)
print numErrors/len(testset)


print "The time taken by the trained classifier to assign labels"
print time.time() - start_time, "seconds"