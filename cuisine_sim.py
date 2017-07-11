import csv
import math
import numpy as np
import pickle
from numpy import linalg as LA

phrases = {}

def preprocess():
	with open('cuisine_sim.csv', 'rb') as csvfile:
		creader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		first_row = True
		for row in creader:
			if first_row:
				first_row = False
				continue
			stats = []
			cols = row[0].split(',')
			rest = cols[1]
			print rest
			# iterate over stats from i=2
			for i in range(2,len(cols)):
				if i==2:
					vec = round(float(cols[i][2:])*1000.0)/1000
				elif i==len(cols)-1:
					vec = round(float(cols[i][:-2])*1000.0)/1000
				else:
					vec = round(float(cols[i])*1000.0)/1000
				stats.append(vec)
			phrases[rest] = stats

	with open('pre_phrases.pickle', 'wb') as p:
		pickle.dump(phrases,p)

def cosineSim():
	# cosine Similarity (d1, d2) =  Dot product(d1, d2) / ||d1|| * ||d2|
	# Dot product (d1,d2) = d1[0] * d2[0] + d1[1] * d2[1] * d1[n] * d2[n]
	# ||d1|| = square root(d1[0]2 + d1[1]2 + ... + d1[n]2)
	# ||d2|| = square root(d2[0]2 + d2[1]2 + ... + d2[n]2)
	simMatrix = []
	pname = []
	for c_major in phrases.keys():
		print "processing %s" % c_major
		pname.append(c_major)
		cosine_sim = []
		norm1 = LA.norm(phrases[c_major])
		for c_other in phrases.keys():
			norm2 = LA.norm(phrases[c_other])
			if c_major==c_other:
				cosine_sim.append(1)
			else:
				cosine_sim.append(round(np.dot(phrases[c_major],phrases[c_other])/(norm1*norm2),5))
		#print cosine_sim
		simMatrix.append(cosine_sim)

	#print simMatrix

	data = []
	for i, row in enumerate(simMatrix):
		for j, s in enumerate(row):
			score = [i, j, s]
			data.append(score)

	with open('phrases_sim.pickle', 'wb') as p:
		pickle.dump(data,p)

	with open('phrases.pickle', 'wb') as p:
		pickle.dump(pname,p)
		

def main():
	preprocess()
	#cosineSim()

if __name__=='__main__':
	main()