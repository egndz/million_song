#!/usr/bin/python

import common
import re

# input: file name
# output: artist_id artist_name
def map(line):
	line_split=re.split("\t",line)
	track_id=line_split[0]
	track_data=json.loads(line_split[1])
		terms=track_data["artist_terms"]
		if len(terms)>0:
			term_frequencies=track_data["artist_terms_freq"]
			artist_name=track_data["artist_name"]
			top_term=0
			for i in range(len(terms)):
				if(term_frequencies[i]>term_frequencies[top_term]):
					top_term=i
			yield(terms[top_term],artist_name)
		h5.close()

def reduce(word, counts):
	yield(word,str(len(counts)))

if __name__ == "__main__":
  common.main(map, reduce)
