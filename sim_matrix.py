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
import pickle
import argparse
from process import Restaurant

cityPath = "Edinburgh_city/*"

def processlda(filtered=False):

	rest_list = glob.glob(cityPath)
	rest2rev = {}
	reviews = []

	# filter 100 restaurant in center of Edinburgh
	if filtered:
		rest_list = make_sample()

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


def cosineSim():
	# cosine Similarity (d1, d2) =  Dot product(d1, d2) / ||d1|| * ||d2|
	# Dot product (d1,d2) = d1[0] * d2[0] + d1[1] * d2[1] * d1[n] * d2[n]
	# ||d1|| = square root(d1[0]2 + d1[1]2 + ... + d1[n]2)
	# ||d2|| = square root(d2[0]2 + d2[1]2 + ... + d2[n]2)
	simMatrix = []
	rls = []
	rj_list = glob.glob('RestJson/*')
	for ip in enumerate(rj_list):
		cosine_sim = []
		rname = ip[1].split('/')[-1].strip(".json")
		rls.append(rname)
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
			simMatrix.append(cosine_sim)

	data = []
	for i, row in enumerate(simMatrix):
		for j, s in enumerate(row):
			score = [i, j, s]
			data.append(score)

	with open('cos_sim_tfidf.json', 'w') as f:
		json.dump({'data': data,'meta': {'restaurants': rls}}, f)

def main(args):
	if args == 'filter':
		processlda(True)
	elif args == 'simMatrix':
		cosineSim()
	else:
		processlda()

if __name__=="__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--filter', action='store_true')
	parser.add_argument('--simMatrix', action='store_true')

	args = parser.parse_args()

	if args.filter:
		main('filter')
	elif args.simMatrix:
		main('simMatrix')
	else:
		main(False)

