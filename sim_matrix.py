import os
import glob
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lda import idfVectorizer
from gensim import models, matutils
import random
import json
import math

cityPath = "50EDN/*"

def processlda():

	rest_list = glob.glob(cityPath)
	rest2rev = {}
	reviews = []

	# extract the first 30 restaurants
	#sample_number = 3
	count = 0
	for rpath in enumerate(rest_list):
		rname = rpath[1].split('/')[-1].strip('.txt')
		rest2rev[rname] = []
		vectorizer = idfVectorizer(rpath[1], 10000)
		reviews.append([str(word) for key, word in vectorizer.id2words.items()])
		count = count + 1
		print "processing %s" % rname

		t0 = time()
		corpus = matutils.Sparse2Corpus(vectorizer.X, documents_columns=False)
		lda = models.ldamodel.LdaModel(corpus, num_topics=10, id2word=vectorizer.id2words)
		print("done in %fs" % (time() - t0))

		output_json = []
		for i, item in enumerate(lda.show_topics(num_topics=10, num_words=100, formatted=False)):
			topic_terms = {term: str(weight) for term, weight in item[1]}
			output_json.append(topic_terms)

		path = os.getcwd()
		if not os.path.exists(path + '/RestJson'):
			os.makedirs(path + '/RestJson')
		os.chdir(path + '/RestJson')
		with open('%s.json' % rname, 'w') as f:
			json.dump(output_json, f)
		os.chdir(path)			

		#if count == sample_number: break
	print count


def cosineSim():
	# cosine Similarity (d1, d2) =  Dot product(d1, d2) / ||d1|| * ||d2|
	# Dot product (d1,d2) = d1[0] * d2[0] + d1[1] * d2[1] * d1[n] * d2[n]
	# ||d1|| = square root(d1[0]2 + d1[1]2 + ... + d1[n]2)
	# ||d2|| = square root(d2[0]2 + d2[1]2 + ... + d2[n]2)
	simMatix = []
	rj_list = glob.glob('RestJson/*')
	for ip in enumerate(rj_list):
		cosine_sim = []
		rname = ip[1].split('/')[-1].strip('.txt')
		# reference restaurant
		with open(ip[1]) as f:
			ref_bagws = json.load(f)[0]
			# iterate over all the restaurants in the list
			for jp in enumerate(rj_list):
				if jp == ip:
					cosine_sim.append(1)
					continue
				# candidate restaurant
				with open(jp[1], 'r') as f2:
					candidate = json.load(f2)[0]
					dot = 0
					norm1 = 0
					norm2 = 0
					# iterate over the words in the referenced restaurant
					for w1, f1 in ref_bagws.items():
						if w1 in candidate.keys():
							dot += float(ref_bagws[w1])*float(candidate[w1])
						norm1 += float(f1)**2
					for w2, f2 in candidate.items():
						norm2 += float(f2)**2
				cosine_sim.append(round(dot/(math.sqrt(norm1)*math.sqrt(norm2)), 5))
			simMatix.append(cosine_sim)

	# print similiarity matrix
	for row in simMatix:
		print row


	# path = os.getcwd()


def main():
	#processlda()
	cosineSim()



if __name__=="__main__":
	main()