import json
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import models
from gensim import matutils
from time import time
import os

class idfVectorizer():

	text = []

	def __init__(self, sample_file, numfeatures):

		self.vectorizer = TfidfVectorizer(max_df=0.5, max_features=numfeatures, min_df=2, stop_words='english', 
			ngram_range=(1,2), use_idf=True)

		with open(sample_file, 'r') as f:
			self.text = f.readlines()

		self.X = self.extract_features()
		self.id2words = self.mapId2Wds() 


	def extract_features(self):		
		t0 = time()
		print("Extracting featrues from the training dataset using a sparse vectorizer")
		X = self.vectorizer.fit_transform(self.text)
		print("done in %fs" % (time() - t0))
		print("n_samples: %d, n_features: %d" % X.shape)
		return X

	def mapId2Wds(self):
		id2words = {}
		# mapping from feature id to actual word
		for i,word in enumerate(self.vectorizer.get_feature_names()):
			id2words[i] = word
		return id2words

def main(K, numfeatures, sample_file, num_display_words, outputfile):
	
	K_clusters = K
	vectorizer = idfVectorizer(sample_file, numfeatures)

	t0 = time()
	print("Applying topic modeling, using LDA")
	print(str(K_clusters) + "topics")
	corpus = matutils.Sparse2Corpus(vectorizer.X, documents_columns=False)
	lda = models.ldamodel.LdaModel(corpus, num_topics=K_clusters, id2word=vectorizer.id2words)
	print("done in %fs" % (time() - t0))

	output_text = []
	# for K_clusters, return num_words_most significant word
	# return as a list - a list of strings if formatted is True, or (word, probability) 2-tuples if False
	for i, item in enumerate(lda.show_topics(num_topics=K_clusters, num_words=num_display_words, formatted=False)):
		output_text.append("Topic: " + str(i))
		for term, weight in item[1]:
			output_text.append(term + ":" + str(weight))

	print "writing topics to file: ", outputfile
	with open (outputfile, 'w') as f:
		f.write('\n'.join(output_text))

	output_json = []
	for i, item in enumerate(lda.show_topics(num_topics=K_clusters, num_words=num_display_words, formatted=False)):
		topic_terms = {term: str(weight) for term, weight in item[1]}
		output_json.append(topic_terms)


if __name__=="__main__":

	# This program takes in a file and some parameters and generates topic modeling from the file. 
	# This program assumes the file is a line corpus, 
	# e.g. list or reviews and outputs the topic with words and weights on the console.'
	parser = argparse.ArgumentParser()

	# K is the number of topics to use when running the LDA algorithm. Default 100.
	parser.add_argument('-K', default=10, type=int)

	# Specifies the file which is used by to extract the topics. 
	# The default file is "review_sample_100000.txt"
	parser.add_argument('-f', dest='path2datafile', default="review_sample_100000.txt")

	# feature is the number of features to keep when mapping the bag-of-words to tf-idf vectors, 
	# (eg. lenght of vectors). Default featureNum=50000
	parser.add_argument('-featureNum', default=50000, type=int)

	# This option specifies how many words to display for each topic. Default is 15 words for each topic.
	parser.add_argument('-displayWN', default=15, type=int)

	# Specifies the output file for the topics, The format is as a topic number followed by a list of words with corresdponding weights of the words. 
	# The default output file is "sample_topics.txt"
	parser.add_argument('-o', dest='outputfile', default="sample_topics.txt")

	args = parser.parse_args()

	print "using input file: ", args.path2datafile
	main(args.K, args.featureNum, args.path2datafile, args.displayWN, args.outputfile)



