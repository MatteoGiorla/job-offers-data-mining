import json
import nltk
import nltk.data as nd
import re
from difflib import SequenceMatcher

with open('databases/SeparatingTerms.json') as sep_terms_file:
	sep_terms = json.load(sep_terms_file)

with open('databases/ListOfCategories.json') as cat_file:
	cat_data = json.load(cat_file)

def add_field_to_JSON(new_key, new_value, filename):
	with open(filename, 'r+') as file:
		data = json.load(file)
		data[new_key] = new_value
		file.seek(0)
		file.truncate(0)
		json.dump(data, file, indent=4)

def search_term_in_sentence(list_of_terms, sentence):
	counter = 0
	for term in list_of_terms:
		for m in re.finditer(term, sentence):
			counter += 1
	return counter

def split_into_sentences(data):
	tokenizer = nd.load('tokenizers/punkt/english.pickle') #using nltk library to split text into sentences
	return tokenizer.tokenize(data)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def search_sep_terms_in_sentence(sep_term_key, sentence):
	counter = 0
	for i in range(len(sep_terms[sep_term_key])):
		search_for = sep_terms[sep_term_key][i]
		for m in re.finditer(search_for, sentence):
			counter += 1
	return counter

def classify_sentence(sentence):
	group1 = search_sep_terms_in_sentence('Responsibilities', sentence)
	group2 = search_sep_terms_in_sentence('Profile', sentence)
	group3 = search_sep_terms_in_sentence('Footer', sentence)
	if group1 == 0 and group2 == 0 and group3 == 0:
		return 0
	elif (group2 >= group1) and (group2 >= 0.5*group3):
		return 2
	elif (group1 > group2) and (group1 >= 0.5*group3):
		return 1
	elif (group3 > group1) and (group3 > group2):
		return 3

def classify_sentences(list_of_sentences):
	list_of_responsibilities_sentences = []
	list_of_profile_sentences = []
	list_of_footer_sentences = []
	list_of_unclassified_sentences = []

	for sentence in list_of_sentences:
		group = classify_sentence(sentence)
		if group == 1:
			list_of_responsibilities_sentences.append(sentence)
		elif group == 2:
			list_of_profile_sentences.append(sentence)
		elif group == 3:
			list_of_footer_sentences.append(sentence)
		else:
			list_of_unclassified_sentences.append(sentence)

	return (list_of_responsibilities_sentences, list_of_profile_sentences, list_of_footer_sentences, list_of_unclassified_sentences)

def sentence_separation_helper(text, word):
	word1_to_replace = '.  your ' + word
	word1_replaced = '. your ' + word + ':'
	word2_to_replace = '  your ' + word
	word2_replaced = '. your ' + word + ':'
	word3_to_replace = '.. your ' + word + ':'
	word3_replaced = '. your ' + word + ':'
	clean_text = text.replace(word1_to_replace, word1_replaced)
	clean_text = clean_text.replace(word2_to_replace, word2_replaced)
	clean_text = clean_text.replace(word3_to_replace, word3_replaced)
	return clean_text

def cleaning_text(text):
	clean_text = ''
	if text != None :
		clean_text = text.lower()
		clean_text = sentence_separation_helper(clean_text, 'profile')
		clean_text = sentence_separation_helper(clean_text, 'tasks')
		clean_text = sentence_separation_helper(clean_text, 'responsabilities')
		clean_text = sentence_separation_helper(clean_text, 'skills')
		clean_text = sentence_separation_helper(clean_text, 'qualities')

		clean_text = clean_text.replace('we offer:', '. we offer:')

		clean_text = clean_text.replace('::', ':')

		clean_text = clean_text.replace('(m / w)', '.')
		clean_text = clean_text.replace('(w / m)', '.')
		clean_text = clean_text.replace('(m / f)', '.')
		clean_text = clean_text.replace('a / n', ' ')

		for i in range(3):
			clean_text = clean_text.replace('  ', ' ')
		clean_text = clean_text.replace(' .', '.')
		clean_text = clean_text.replace('.. ', '. ')

		#to be able to distinguish c from c++ or c#
		clean_text = clean_text.replace('c ++', 'c++')
		clean_text = clean_text.replace('c #', 'c#')
	return clean_text

def stemming(text):
	tokens = nltk.word_tokenize(text)
	porter = nltk.PorterStemmer()
	stem_text = ' '.join([porter.stem(t) for t in tokens])
	return stem_text

def get_words(list_of_sentences):
	words = list_of_sentences.split()
	return words

def search_skill_in_text(search_for, text):
	if search_for in text:
		return True
	return False