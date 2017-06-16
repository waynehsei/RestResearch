import math
import json
import pickle
import random
import argparse
import os
import shutil
from abc import ABCMeta, abstractmethod

path2files="YelpChallenge/"
path2business=path2files+"yelp_academic_dataset_business.json"
path2reviews=path2files+"yelp_academic_dataset_review.json"

class Restaurant:

	categories = set([])
	reviews = []
	texts = []

	def __init__(self, name, rid, city, star, latitude, longitude):
		self.rid = rid
		self.city = city
		self.star = star
		self.name = name
		self.latitude = latitude
		self.longitude = longitude

	def addCat(self, cats):
		self.categories = set(cats).union(self.categories) - set(['Restaurants'])

	def addRev(self, revID):
		self.reviews.append(revID)

	def addText(self, text):
		self.texts.append(text.replace('\n', ' ').strip())


class Factory:
	__metaclass__ = ABCMeta
	restaurants = {}
	@abstractmethod
	def add(self, rest):
		pass

class CityRest(Factory):
	def add(self, rest):
		if rest.city not in self.restaurants:
			self.restaurants[rest.city] = {}
		self.restaurants[rest.city][rest.rid] = rest


class CatRest(Factory):
	# add rid into category
	def add(self, rest):
		for cat in rest.categories:
			if cat in self.restaurants:
				self.restaurants[cat].append(rest)
			else:
				self.restaurants[cat] = [rest]

def main(args):

	r = 'Restaurants'
	rest2rid = {}
	rate2review = {}

	def save_restaurant(add):
		factory = add()
		with open(path2business, 'r') as f:
			for line in f.readlines():
				business_json = json.loads(line)
				if business_json['city'] == "Edinburgh" or business_json['city'] == "City of Edinburgh":
					bjc = business_json['categories']
					if bjc == None:
						continue
					if r in bjc:
						if len(bjc) > 1:
							rest = Restaurant(business_json['name'], business_json['business_id'], business_json['city'], business_json['stars'], business_json['latitude'], business_json['longitude'])
							#rest.addCat(business_json['categories'])
							rest2rid[rest.rid] = rest
							factory.add(rest)
			f.close()

		print "saved restaurant information"
		return factory

	# Rating with all comment with same star
	if args == "rev_star":
		# process review data
		with open(path2reviews, 'r') as f:
			for line in f.readlines():
				review_json = json.loads(line)
				rstar = review_json['stars']
				if review_json['business_id'] in rest2rid:
					rest2rid[review_json['business_id']].addRev(review_json['review_id'])
					if rstar not in rate2review:
						rate2review[rstar] = []
					rate2review[rstar].append(review_json['text'].replace('\n', ' ').strip())
			f.close()

		with open('data_rate2review.pickle', 'wb') as f:
			pickle.dump(rate2review,f)

		with open("all_reviews.txt", 'w') as f:
			for star, reviews in rate2review.items():
				f.write('\n'.join(reviews).encode('ascii', 'ignore'))
				f.write('\n')

				with open("all_reviews_star_%d.txt" % star, 'w') as f2:
					f2.write('\n'.join(reviews).encode('ascii', 'ignore'))
				f2.close()
			f.close()

	# Category with corresponding reviews
	if args == "rev_cuisine":
		cat2rev = {}
		# cuisine_nb = 5
		# cuisine_sample = []
		iirev = {}
		factory = save_restaurant(CatRest)
		with open(path2reviews, 'r') as f:
			for line in f.readlines():
				review_json = json.loads(line)
				# append review id to restaurant object
				if review_json['business_id'] in rest2rid:
					for cat in rest2rid[review_json['business_id']].categories:
						if cat == 'Italian' or cat == 'Indian':
							if cat not in cat2rev:
								cat2rev[cat] = []
								iirev[cat] = {}
							cat2rev[cat].append(review_json['text'].replace('\n', ' ').strip())
							if review_json['stars'] not in iirev[cat]:
								iirev[cat][review_json['stars']] = 0
							iirev[cat][review_json['stars']] += 1
			f.close()
		
		with open('data_cat2review.pickle', 'wb') as f:
			pickle.dump(cat2rev,f)

		# cuisine_sample = random.sample(cat2rev, cuisine_nb)
		for cat in cat2rev:
			print cat
			with open('review_%s.txt' % cat, 'w') as f:
				f.write('\n'.join(cat2rev[cat]).encode('ascii', 'ignore'))
			f.close()

		with open('IT_ID_reviewCount.txt', 'w') as f:
			for cat in iirev:
				f.write(cat + "\n")
				for rate in iirev[cat]:
					f.write(str(rate) + ": " + str(iirev[cat][rate]) + "\n")
			f.close()

	# Restaurants in same city with reviews
	if args == "city_rest":
		factory = save_restaurant(CityRest)
		with open(path2reviews, 'r') as f:
			for line in f.readlines():
				review_json = json.loads(line)
				for city in factory.restaurants:
					if review_json['business_id'] in factory.restaurants[city]:
						factory.restaurants[city][review_json['business_id']].addText(review_json['text'])
			f.close()

		with open('data_edinburg_rest.pickle', 'wb') as f:
			pickle.dump(factory.restaurants,f)

		path = os.getcwd()
		os.makedirs(path + "/Edinburgh_city")
		os.chdir(path + "/Edinburgh_city")
		for city in factory.restaurants:
			print city
			for rid in factory.restaurants[city]:
				r = factory.restaurants[city][rid]
				rname = r.name.replace('/', ' ')
				with open('%s.txt' % rname, 'w') as f:
					f.write('\n'.join(r.texts).encode('ascii', 'ignore'))
				f.close()
			#os.chdir(f_path)
		print "processed restaurants in city"

	# filter endinburgh city in city center
	if args == "filter":
		rcount = 0
		candidate = []
		edin_rest = pickle.load(open('data_edinburg_rest.pickle', 'rb'))
		for city in edin_rest:
			for rid, rest in edin_rest[city].items():
				if -3.209209 < rest.longitude < -3.179469 and 55.944093 < rest.latitude < 55.956539:
					rcount += 1
					#rname = rest.name.replace('/', ' ')
					candidate.append(rest)
		#rcount = 569
		sample_edn = random.sample(candidate, 100)

		path = os.getcwd()
		os.makedirs(path + "/sample_path")
		for r in sample_edn:
			os.chdir(path + "/sample_path")
			with open('%s.txt' % r.name.replace('/', ' '), 'w') as f:
				f.write('\n')
			os.chdir(path)

		with open('sample_edinburg.pickle', 'wb') as f:
			pickle.dump(sample_edn,f)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--star', action='store_true')
	parser.add_argument('--cuisine', action='store_true')
	parser.add_argument('--city', action='store_true')
	parser.add_argument('--filter', action='store_true')

	args = parser.parse_args()

	if args.star:
		print "processing restaurants by stars"
		main("rev_star")
	elif args.cuisine:
		print "processing restaurants by cuisines"
		main("rev_cuisine")
	elif args.city:
		print "processing restaurants by city"
		main("city_rest")
	elif args.filter:
		main("filter")










