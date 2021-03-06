#!/usr/bin/python

import common
import json
import sys
import numpy
import re
import os
import glob

# input: songs (possibly to classify)
# output: categories, category_prediction_percentage
def map(line):
	line_split=re.split("\t",line)
	track_id=line_split[0]
	track_data=json.loads(line_split[1])
	artist_id=track_data["artist_id"]
	if(not artist_dict.has_key(artist_id)):
		# find the actual term we're looking for
		artist_terms=track_data["artist_terms"]
		if len(artist_terms)>0:
			term_frequencies=track_data["artist_terms_freq"]
			top_term=0
			for i in range(len(artist_terms)):
				if(term_frequencies[i]>term_frequencies[top_term]):
					top_term=i
			actual_term=artist_terms[top_term]	
			# we only want to do this if it's one of the categories we classify
			if actual_term in classifier.keys():
				# make data array for this track
				data_for_key=[]
				for data_name in interesting_data_names:
					if(getattr(track_data[data_name],'__iter__',False)):
						for data in track_data[data_name]:
							data_for_key.append(data)
					else:
						data_for_key.append(track_data[data_name])
				data_for_key_array=numpy.array(data_for_key)
				# figure out which category gives us the top classifier
				top_probability_term=actual_term # initialize top term
				top_probability=-1000
				for classifier_term,classifier_data in classifier.items():
					probabilities=[]
					v=numpy.array(classifier_data)
					term_probability=numpy.dot(v,data_for_key_array.T)-threshold[classifier_term]
#					print classifier_term+"\t"+str(term_probability)
					if term_probability>top_probability:
						top_probability=term_probability
						top_probability_term=classifier_term
				if top_probability==-1000:
					top_probability_term="unknown"
				yield("1",actual_term+","+top_probability_term+","+str(top_probability))
		
# output: actual category, correct prediction %, wrong prediction %
def reduce(word, counts):
	false_positives={}
	false_negatives={}
	correct={}
	for key in classifier.keys():
		correct[key]=0
		false_positives[key]=0
		false_negatives[key]=0
	false_positives["unknown"]=0
	for count in counts:
		count_split=re.split(",",count)
		actual_term=count_split[0]
		top_probability=count_split[1]
#		print actual_term+" "+top_probability
		# we only want to do this if it's one of the categories we classify
		if classifier.has_key(actual_term):
			# and classify into correct/incorrect buckets
			if(top_probability==actual_term):
				correct[actual_term]+=1
#				print "****MATCH****"+str(correct[actual_term])
			else:
				false_positives[top_probability]+=1
				false_negatives[actual_term]+=1
#				print "****WRONG****"+str(false_positives[top_probability])+" "+str(false_negatives[actual_term])
	for term in classifier.keys():
		yield_string=str(correct[term]+false_negatives[term])+"\t"+str(correct[term])+"\t"+str(false_negatives[term])+"\t"+str(false_positives[term])
		yield(term,yield_string)		

if __name__ == "__main__":
	global interesting_data_names
	# removing hottness for now because it keeps us from inverting our matricies
	interesting_data_names=["duration","num_bars","variance_bar_length","num_beats",
			"variance_beats_length","danceability","end_of_fade_in","energy","key","loudness","mode",
			"num_sections","variance_sections_length","num_segments","variance_segments_length",
			"segment_loudness_max","segment_loudness_time","segment_loudness_mean",
			"segment_loudness_variance","segment_pitches_mean","segment_pitches_variance",
			"segment_timbres_mean","segment_timbres_variance","fade_out","num_tatums",
			"variance_tatums_length","tempo","time_signature","year"]
	# create dictionary of test artists
	global artist_dict
	artist_dict={}
	f = open("artists_train.txt",'r')
	for artist in f:
		artist_dict[artist.rstrip()]=1
	f.close()
	# import our classifier
	# we want to iterate over all files starting with "part" in the directory
	# code from http://bogdan.org.ua/2007/08/12/python-iterate-and-read-all-files-in-a-directory-folder.html
	global classifier
	global threshold
	classifier={}
	threshold={}
	path = 'build_fisher/'
	for infile in glob.glob( os.path.join(path, 'part*') ):
		f = open(infile,'r')
		for classifier_line in f:
			classifier_line_split=re.split("\t",classifier_line.rstrip())
			classifier_data_split=re.split(",",classifier_line_split[1],maxsplit=1)
			threshold[classifier_line_split[0]]=float(classifier_data_split[0])
			classifier[classifier_line_split[0]]=json.loads(classifier_data_split[1])
		f.close()
	common.main(map, reduce)
