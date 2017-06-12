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

	def __init__(self, rid, city, star):
		self.rid = rid
		self.city = city
		self.star = star

	def addCat(self, cats):
		self.categories = set(cats).union(self.categories) - set(['Restaurants'])

	def addRev(self, revID):
		self.reviews.append(revID)

class Factory:
	__metaclass__ = ABCMeta
	restaurants = {}
	@abstractmethod
	def add(self, rest):
		pass

class CityRest(Factory):
	def add(self, rest):
		if rest.city in self.restaurants:
			self.restaurants[rest.city].append(rest)
		else:
			self.restaurants[rest.city] = [rest]

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
def main():

	r = 'Restaurants'
	rest2rid = {}

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
						rest = Restaurant(business_json['business_id'], business_json['city'], business_json['stars'])
						rest.addCat(business_json['categories'])
						rest2rid[rest.rid] = rest
						factory.add(rest)
			f.close()

		print "saved restaurant information"

	# # restaurant id with rating sorted by city
	# with open('restaurantIds2ratings.txt', 'w') as f:
	# 	for key in factory.city2rid:
	# 		for item in factory.city2rid[key]:
	# 			f.write(item.rid + " " + str(item.star) + "\n")
	# 	f.close()

	save_restaurant(CityRest)

	# if rev_star:
	rate2review = {}
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

	with open("all_reviews.txt", 'w') as f:
		for star, reviews in rate2review.items():
			f.write('\n'.join(reviews).encode('ascii', 'ignore'))
			f.write('\n')

			with open("all_reviews_star_%d.txt" % star, 'w') as f2:
				f2.write('\n'.join(reviews).encode('ascii', 'ignore'))
			f2.close()
		f.close()




if __name__ == "__main__":
	main()










