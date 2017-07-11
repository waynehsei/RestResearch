import csv
import pickle
from nltk.tokenize import word_tokenize, sent_tokenize

path = 'cuisines/review_Himalayan-Nepalese.txt'

phrases = []

def words2one():
	with open('salient.csv', 'rb') as csvfile:
		wordsReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in wordsReader:
			stat = row[0].split(',')
			if stat[1] >= 0.8:
				words = stat[0].split('_')
				word = {words[0]: words[1]}
				phrases.append(word)
				print word

	with open('word2one.pickle', 'wb') as p:
		pickle.dump(phrases, p)

def covert():
	count = 0
	result = []
	phrases = pickle.load(open('word2one.pickle', 'rb'))
	with open(path, 'r') as txtfile:
		for line in txtfile.readlines():
			line = line.strip().decode('utf-8')
			list_of_words = [word_tokenize(sent) for sent in sent_tokenize(line)]
			print list_of_words
		# 	for i, w in enumerate(list_of_words):
		# 		try:
		# 			if w in phrases and phrases[w]==list_of_words[i+1]:
		# 				list_of_words[i] = w+"_"+w[i+1]
		# 				count+=1
		# 				print list_of_words[i]
		# 		except:
		# 			print "out of boundary exception"
		# result.append(line)

def main():
	#words2one()
	covert()

if __name__=='__main__':
	main()


