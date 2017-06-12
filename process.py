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
path2reviews=path2files+"yelp_review_1_to_1000.json"

class Restaurant:

	categories = set([])
	reviews = []
	texts = []

	def __init__(self, name, rid, city, star):
		self.rid = rid
		self.city = city
		self.star = star
		self.name = name

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

# class Factory:

# 	city2rid = {}
# 	cat2rid = {}
# 	star2rid = {}

# 	def catRid(self, rest):
# 		# add rid into category
# 		for cat in rest.categories:
# 			if cat in self.cat2rid:
# 				self.cat2rid[cat].append(rest)
# 			else:
# 				self.cat2rid[cat] = [rest]

# 	def cityRid(self, rest):
# 		if rest.city in self.city2rid:
# 			self.city2rid[rest.city].append(rest)
# 		else:
# 			self.city2rid[rest.city] = [rest]

# 	def byStar(self, rest):
# 		if rest.star in self.star2rid:
# 			self.star2rid[rest.star].append(rest)
# 		else:
# 			self.star2rid[rest.star] = [rest]

# 	def add(self, rest):
# 		#self.catRid(rest)
# 		#self.cityRid(rest)
# 		self.byStar(rest)

# rev_star, rev_cuisine
def main(args):

	r = 'Restaurants'
	rest2rid = {}
	rate2review = {}

	def save_restaurant(add):
		factory = add()
		with open(path2business, 'r') as f:
			for line in f.readlines():
				business_json = json.loads(line)
				bjc = business_json['categories']
				if bjc == None:
					continue
				if r in bjc:
					if len(bjc) > 1:
						rest = Restaurant(business_json['name'], business_json['business_id'], business_json['city'], business_json['stars'])
						rest.addCat(business_json['categories'])
						rest2rid[rest.rid] = rest
						factory.add(rest)
			f.close()

		with open('data_rest2rid.pickle', 'wb') as f:
			pickle.dump(rest2rid,f)

		# with open('restaurantIds2ratings.txt', 'w') as f:
		# 	for key in factory.city2rid:
		# 		for item in factory.city2rid[key]:
		# 			f.write(item.rid + " " + str(item.star) + "\n")
		# 	f.close()
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

		path = os.getcwd()
		os.makedirs(path + "/restaurants")
		os.chdir(path + "/restaurants")
		for city in factory.restaurants:
			f_path = os.getcwd()
			if not os.path.exists(f_path + "/%s" % city):
				os.makedirs(f_path + "/%s" % city)
			os.chdir(f_path + "/%s" % city)
			print os.getcwd()
			for rid in factory.restaurants[city]:
				r = factory.restaurants[city][rid]
				rname = r.name.replace('/', ' ')
				with open('%s.txt' % rname, 'w') as f:
					f.write('\n'.join(r.texts).encode('ascii', 'ignore'))
				f.close()
			os.chdir(f_path)
		print "processed restaurants in city"

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--star', action='store_true')
	parser.add_argument('--cuisine', action='store_true')
	parser.add_argument('--city', action='store_true')

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










