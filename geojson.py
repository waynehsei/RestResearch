import argparse
import json
import pickle
import glob
from process import Restaurant
from collections import OrderedDict

def simple_test(rls, cluster, output):
	r_to_c = {}
	for i, r in enumerate(rls):
		r_to_c[r] = cluster[i]
	for key, item in output.items():
		try:
			if item[1] != r_to_c[item[0].name]:
				print False
		except:
			print item


def main(path='./cos_sim_tfidf.json'):

	sample_data = []
	sample = glob.glob("RestJson/*")
	data_edinburg = pickle.load(open('data_edinburg_rest.pickle', 'rb'))
	sample_edinburg = []
	for city, r in data_edinburg.items():
		sample_edinburg += r.values()
	# sample_edinburg = [r for city, r in data_edinburg.items()]

	data = None
	with open(path) as f:
		data = json.load(f)

	cluster = data["cluster"]
	# in json, there's 104 files, while in sample only 100
	rls = data["meta"]["restaurants"]
	print len(rls)
	rest2cluser = {}
	for rest in sample_edinburg:
		if rest.name in rls:
			rest2cluser[rest.name] = [rest]
			try:
				if rest.name.decode('utf-8') in rls:
					rest2cluser[rest.name].append(cluster[rls.index(rest.name)])
			except:
				print rest.name
				for i, r in enumerate(rls):
					try:
						r.decode('utf-8')
					except:
						rest2cluser[rest.name].append(cluster[i])
						continue
	print len(rest2cluser)

	# convert to geojson
	geojson = {"features":[], "type":"FeatureCollection"}
	for key, item in rest2cluser.items():
		restaurant = item[0]
		cluster = item[1]
		a = (("type","Feature"),("properties", {"restaurant": restaurant.name, "cluster": cluster}),
			("geometry",{"coordinates":[restaurant.longitude, restaurant.latitude],"type":"Point"}))
		info = OrderedDict(a)
		geojson["features"].append(info)

	
	geojson_path = path[:-5] + ".geojson"
	with open(geojson_path, 'w') as f:
		json.dump(geojson,f)

if __name__=="__main__":
	main()


