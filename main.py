import json
import nltk
import nltk.data as nd
import os
import glob
import sys
import fnmatch
from collections import Counter
from itertools import combinations

import helper_functions

path = 'data/'
write_path_graph = 'graph/data/'

tt_key = 'TranslatedText'
category_key = 'Category'

number_of_empty_files = 0
number_of_empty_translated_text = 0
number_of_bad_cat = 0
number_of_bad_json_formatting = 0

with open('databases/ListOfCategories.json') as cat_file:
	cat_data = json.load(cat_file)
list_of_categories = cat_data['Categories']

with open('databases/SkillsDatabase.json') as skills_db:
	skills_db = json.load(skills_db)
with open('databases/GeneralQualitiesDatabase.json') as gen_qualities_db:
	gen_qualities_db = json.load(gen_qualities_db)
with open('databases/DiplomaDatabase.json') as diploma_db:
	diploma_db = json.load(diploma_db)

total_number_of_files = len(fnmatch.filter(os.listdir(path), '*.json'))
files_done = 0

for filename in glob.glob(os.path.join(path, '*.json')):
	if os.stat(filename).st_size != 0:
		preprocessed_text = ''
		stem = ''
		list_of_sentences = []
		list_of_responsibilities_sentences = []
		list_of_profile_sentences = []
		list_of_footer_sentences = []
		list_of_unclassified_sentences = []
		skills_list = []
		general_qualities_list = []
		diploma_list = []

		with open(filename) as data_file:
			data = json.load(data_file)
			if tt_key in data:
				if category_key in data:
					translated_text = data[tt_key]
					if translated_text != None:
						category = data[category_key]
						if category in list_of_categories:

							#============================#
							# Preprocessing and clean up #
							#============================#

							preprocessed_text = helper_functions.cleaning_text(translated_text)
							
							#Stemming using PorterStemmer
							stem = helper_functions.stemming(preprocessed_text)

							if preprocessed_text != None:
								#Split preprocessed text into sentences
								list_of_sentences = helper_functions.split_into_sentences(preprocessed_text)

								sentences_to_discard = set()

								#suppress very short sentences as they are always junk
								for sent in list_of_sentences:
									if len(sent) <= 15:
										list_of_sentences.remove(sent)

								list_of_sentences = list(set(list_of_sentences))

								#suppress duplicate sentences
								for i in range(len(list_of_sentences)):
									for j in range(len(list_of_sentences)):
										if i != j:
											similarity = helper_functions.similar(list_of_sentences[i], list_of_sentences[j])
											if similarity >= 0.6:
												if(len(list_of_sentences[i]) >= len(list_of_sentences[j])):
													sentences_to_discard.add(list_of_sentences[j])
												else:
													sentences_to_discard.add(list_of_sentences[i])

								for sent in list_of_sentences:
									#suppress javascript/html code
									list_of_terms = ['javascript: style', 'framebox', 'layout type', 'html class', 'width: expression', 
									'print advertisement', 'width', 'button', 'onmouseover', 'href', '&amp; gt; &amp; lt; br &amp;', 
									'subnavigation', '404 error', 'xpert.rec']
									if helper_functions.search_term_in_sentence(list_of_terms, sent) > 0:
										sentences_to_discard.add(sent)

								list_of_sentences = list(set(list_of_sentences))

								for elem in sentences_to_discard:
									list_of_sentences.remove(elem)

							#==============#
							# Partitioning #
							#==============#

							(list_of_responsibilities_sentences, list_of_profile_sentences, list_of_footer_sentences, list_of_unclassified_sentences) = helper_functions.classify_sentences(list_of_sentences)

							#====================#
							# Extract the skills #
							#====================#

							if list_of_profile_sentences != None:
								skills_list = set()
								general_qualities_list = set()
								diploma_list = set()

								profile_text = ' '.join(list_of_profile_sentences)

								for k1, v1 in skills_db.items():
									for skill in v1:
										if helper_functions.search_skill_in_text(skill, profile_text):
											skills_list.add(k1)
								for k2, v2 in gen_qualities_db.items():
									for gen_quality in v2:
										if helper_functions.search_skill_in_text(gen_quality, profile_text):
											general_qualities_list.add(k2)
								for k3, v3 in diploma_db.items():
									for diploma in v3:
										if helper_functions.search_skill_in_text(diploma, profile_text):
											diploma_list.add(k3)
								
								skills_list = list(skills_list)
								if category != 'IT, Telecommunications' and category != 'Electronics, Engineering' and category != 'Graphics, Printing':
									if 'C' in skills_list:
										skills_list.remove('C')
									if 'R' in skills_list:
										skills_list.remove('R')

								general_qualities_list = list(general_qualities_list)
								diploma_list = list(diploma_list)

						else:
							number_of_bad_cat += 1
					else:
						number_of_empty_translated_text += 1
				else:
					number_of_bad_cat += 1

			else:
				number_of_empty_translated_text += 1

		#==============================#
		# Write data to the JSON files #
		#==============================#

		helper_functions.add_field_to_JSON('PreprocessedText', preprocessed_text, filename)
		helper_functions.add_field_to_JSON('Stemming', stem, filename)
		helper_functions.add_field_to_JSON('ListOfSentences', list_of_sentences, filename)
		helper_functions.add_field_to_JSON('Responsibilities', list_of_responsibilities_sentences, filename)
		helper_functions.add_field_to_JSON('Profile', list_of_profile_sentences, filename)
		helper_functions.add_field_to_JSON('Footer', list_of_footer_sentences, filename)
		helper_functions.add_field_to_JSON('Unclassified', list_of_unclassified_sentences, filename)
		helper_functions.add_field_to_JSON('Skills', skills_list, filename)
		helper_functions.add_field_to_JSON('GeneralQualities', general_qualities_list, filename)
		helper_functions.add_field_to_JSON('Diploma', diploma_list, filename)

	else:
		number_of_empty_files += 1

	files_done += 1
	print('Extracting skills :', files_done, 'of', total_number_of_files, 'files done.', end='\r')


print('Extracting skills :', files_done, 'of', total_number_of_files, 'files done.')

#==================#
# Create the graph #
#==================#

percent_graph_done = 0
print('Generating the graph : %.2f%% done.' %(percent_graph_done), end='\r')

#RED COLORS
skill_color = ["rgba(232, 69, 60)",
				"rgba(233, 79, 71)",
				"rgba(234, 91, 83)",
				"rgba(236, 102, 95)",
				"rgba(237, 113, 106)",
				"rgba(239, 124, 118)",
				"rgba(240, 132, 126)",
				"rgba(242, 147, 141)",
				"rgba(243, 158, 153)",
				"rgba(244, 169, 165)"]
#color for histogram
H_SKILL_COLOR = 1;

#YELLOW COLORS
qual_color = ["rgba(249, 187, 45)",
				"rgba(249, 191, 57)",
				"rgba(249, 195, 70)",
				"rgba(250, 199, 82)",
				"rgba(250, 203, 95)",
				"rgba(251, 207, 107)",
				"rgba(251, 210, 116)",
				"rgba(251, 215, 133)",
				"rgba(252, 219, 145)",
				"rgba(252, 224, 158)"]
#color for histogram
H_QUAL_COLOR = 2;

#BLUE COLORS
dipl_color = ["rgba(70, 136, 241)",
				"rgba(80, 143, 241)",
				"rgba(92, 150, 242)",
				"rgba(103, 157, 243)",
				"rgba(114, 164, 244)",
				"rgba(125, 171, 245)",
				"rgba(133, 176, 246)",
				"rgba(147, 186, 247)",
				"rgba(158, 193, 248)",
				"rgba(170, 200, 249)"]
#color for histogram
H_DIPL_COLOR = 3;

#GRAY COLOR
gray_color = "rgba(239, 240, 240)"

#color for histogram (default)
H_GRAY_COLOR = 0;

key_skills = 'Skills'
key_qual = 'GeneralQualities'
key_diploma = 'Diploma'
key_category = 'Category'

selected_category = ''
ignore_category = False

for s in range(4):
	graph_filename = ''
	if s == 0:
		graph_filename = 'a'
	elif s == 1:
		graph_filename = 's'
	elif s == 2:
		graph_filename = 'q'
	elif s == 3:
		graph_filename = 'd'

	for c in range(19):
		if c == 0:
			final_graph_filename = graph_filename + 'a.json'
			ignore_category = True
		else:
			selected_category = list_of_categories[c-1]
			final_graph_filename = graph_filename + str(c) + '.json'
			ignore_category = False

		#initialize counters
		graph_skills = []
		graph_skills_relations = []

		for filename in glob.glob(os.path.join(path, '*.json')):
			if os.stat(filename).st_size != 0:
				with open(filename) as data_file:
					data = json.load(data_file)

					#select category
					if key_category in data:
						if data[key_category] == selected_category or ignore_category:
							
							#select skills category (all, skills, qualities or diploma)
							this_job_skills = []
							if s == 0 :
								data_skills = data[key_skills]
								this_job_skills.extend(data_skills)
								data_qual = data[key_qual]
								this_job_skills.extend(data_qual)
								data_diploma = data[key_diploma]
								this_job_skills.extend(data_diploma)
							elif s == 1 :
								data_skills = data[key_skills]
								this_job_skills.extend(data_skills)
							elif s == 2 :
								data_qual = data[key_qual]
								this_job_skills.extend(data_qual)
							elif s == 3 :
								data_diploma = data[key_diploma]
								this_job_skills.extend(data_diploma)
							else:
								print('error')
							graph_skills.extend(this_job_skills)

							#edges
							if this_job_skills:
								edges = list(combinations(this_job_skills, 2))
								for elem in edges:
									graph_skills_relations.append(frozenset(elem))

		#count skills
		skills_counts = Counter(graph_skills)
		total_size_of_nodes = len(graph_skills);

		#count edges
		SELECTED_EDGES_COEFFICIENT = 0.0008
		relations_counts = Counter(graph_skills_relations).most_common()
		total_size_of_edges = len(graph_skills_relations);

		only_most_common = []
		for elem in relations_counts:
			if elem[1] > SELECTED_EDGES_COEFFICIENT * total_size_of_edges:
				only_most_common.append(elem)

		#node and edge dictionaries
		graph_data = {}
		edges_list = []
		nodes_list = []
		histogram_list = []
		tmp_nodes_in_edges = set()
		
		#fix parameters of edges
		number_color = 0
		i = 0
		number_of_edges_by_color = len(only_most_common) / 10;

		for elem in only_most_common:
			elem1, elem2 = elem[0]
			tmp_nodes_in_edges.add(elem1)
			tmp_nodes_in_edges.add(elem2)
			edge_elems = {}
			edge_elems['id'] = str(i)
			edge_elems['source'] = elem1
			edge_elems['target'] = elem2
			#fix color
			if elem1 in skills_db and elem2 in skills_db:
				color = skill_color[int(number_color/number_of_edges_by_color)]
				number_color += 1
			elif elem1 in gen_qualities_db and elem2 in gen_qualities_db:
				color = qual_color[int(number_color/number_of_edges_by_color)]
				number_color += 1
			elif elem1 in diploma_db and elem2 in diploma_db:
				color = dipl_color[int(number_color/number_of_edges_by_color)]
				number_color += 1
			else:
				color = gray_color
				number_color += 1

			edge_elems['color'] = color
			edge_elems['size'] = str(elem[1])
			edges_list.append(edge_elems)
			i += 1

		graph_data['edges'] = list(reversed(edges_list))

		#fix parameters of nodes
		for elem in skills_counts:
			if elem in tmp_nodes_in_edges:
				node_elems = {}
				node_elems['id'] = elem
				node_elems['label'] = elem
				#fix color
				if elem in skills_db:
					color = skill_color[0]
				elif elem in gen_qualities_db:
					color = qual_color[0]
				elif elem in diploma_db:
					color = dipl_color[0]
				else:
					color = gray_color

				node_elems['color'] = color
				node_elems['size'] = str(skills_counts[elem])
				node_elems['x'] = '0'
				node_elems['y'] = '0'
				nodes_list.append(node_elems)

		graph_data['nodes'] = nodes_list

		#fix parameters of histogram
		for elem in skills_counts:
			histogram_elems = {}
			histogram_elems['label'] = elem
			#fix color
			if elem in skills_db:
				histogram_color = H_SKILL_COLOR
			elif elem in gen_qualities_db:
				histogram_color = H_QUAL_COLOR
			elif elem in diploma_db:
				histogram_color = H_DIPL_COLOR
			else:
				histogram_color = H_GRAY_COLOR

			histogram_elems['histogram_color'] = histogram_color
			histogram_elems['size'] = str(skills_counts[elem])
			histogram_list.append(histogram_elems)

		graph_data['histogram'] = histogram_list

		#write graph file
		try:
			os.remove(final_graph_filename)
		except OSError:
			pass
		with open(write_path_graph+final_graph_filename, 'w') as outfile:
			json.dump(graph_data, outfile)

		percent_graph_done += 1.32
		sys.stdout.write("\033[K")
		print('Generating the graph : %.2f%% done.' %(percent_graph_done), end='\r')

sys.stdout.write("\033[K")
print('Generating the graph : 100% done.\n')

#==============#
# Done / Stats #
#==============#

if number_of_empty_files != 0:
	print('Number of empty files : ', number_of_empty_files)
if number_of_empty_translated_text != 0:
	print('Number of files without TranslatedText field : ', number_of_empty_translated_text)
if number_of_bad_cat != 0:
	print('Number of files without correct category : ', number_of_bad_cat)