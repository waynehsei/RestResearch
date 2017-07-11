import argparse
import gensim
import nltk

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

class RestReviews(object):
	#nltk.download()
	stops = stopwords.words('english')
	def __init__(self, path):
		self.path = path

	def __iter__(self):
		with open(self.path) as f:
			for line in f:
				line = line.strip().decode('utf-8')
				for sent in sent_tokenize(line):
					yield [i.lower() for i in word_tokenize(sent) if i.lower() not in RestReviews.stops]

def processLabel(path):
	pos = []
	neg = []
	with open(path) as f:
		for line in f:
			token, label = line.strip().split('\t')
			token = '_'.join(token.split())
			if int(label):
				pos.append(token)
			else:
				neg.append(token)
	return (pos, neg)

def main(args):

	input_path = 'Edinburgh_city/9 Cellars.txt'
	model_path = 'word2vec.9_Cellars.model'
	label_path = '/9_Cellars.label'

	if args == 'train_phrase':
		ngramNum = 2

		rr = RestReviews(input_path)

		ngram = None
		for i in range(ngramNum - 1):
			ngram = gensim.models.Phrases(rr)
			print 'a'

		model = gensim.models.Word2Vec(rr, workers=6)
		model.save(model_path)

	if args == 'label':
		model = gensim.models.Word2Vec.load(model_path)
		labelpos, labelneg = processLabel(label_path)
		labelpos = set(labelpos) & set(model.vocab.keys())
		labelneg = set(labelneg) & set(model.vocab.keys())

		mostSim = model.most_similar(
			positive=labelpos,
			negative=labelneg)

		newDishes = [i[0] for i in mostSim if len(i[0].split('_')) > 1]
		for dish in list(newDishes)[:20]:
			print dish




if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()

	parser.add_argument('-train_phrase', action='store_true')
	parser.add_argument('-label', action='store_true')

	args = parser.parse_args()

	if args.train_phrase:
		main('train_phrase')
	elif args.label:
		main('label')




