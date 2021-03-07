import nltk

stopwords = nltk.corpus.stopwords.words("english")
words = [w for w in nltk.corpus.state_union.words() if w.isalpha() and (w.lower() not in stopwords)]

fd = nltk.FreqDist(words)
print(fd.tabulate(5))