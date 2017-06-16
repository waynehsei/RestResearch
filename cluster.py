import argparse
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial import distance
from scipy.sparse import csr_matrix
import json

def main(cluster_algorithm, n_clusters, path):

	data = None
	with open(path) as f:
		data = json.load(f)
	dist = []
	cols = []
	rows = []
	for (row, col, val) in data['data']:
		dist.append(val)
		cols.append(col)
		rows.append(row)

		if row == col: continue

		dist.append(val)
		cols.append(row)
		rows.append(col)

	size = len(data['meta']['restaurants'])

	if cluster_algorithm == 'agglomerative':
		cluster = AgglomerativeClustering(n_clusters=n_clusters)
	
	if cluster_algorithm == 'kmeans':
		cluster = KMeans(n_clusters=n_clusters)

	result = data
	new_data = csr_matrix((dist, (rows, cols)), shape=(size, size))
	cluster.fit(new_data.toarray())
	result['cluster'] = cluster.labels_.tolist()
	with open(path, 'w') as f:
		json.dump(result, f)

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--agglomerative', action='store_true')
	parser.add_argument('--kmeans', action='store_true')
	parser.add_argument('-K', default=3, type=int)
	# parser.add_argument('p', dest='path', default='cos_sim_tfidf.json')

	args = parser.parse_args()

	if args.agglomerative:
		print "Clustering in Agglomerative"
		main("agglomerative", args.K, './cos_sim_tfidf.json')
	elif args.kmeans:
		print "Clusering in KMeans"
		main("kmeans", args.K, './cos_sim_tfidf.json')



