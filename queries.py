import json

def multi_match(query, fields=['title','song_lyrics'], operator ='or'):
	q = {
		"query": {
			"multi_match": {
				"query": query,
				"fields": fields,
				"operator": operator,
				"type": "best_fields"
			}
		}
	}
	return q

def agg_multi_match_q(query, fields=['title','song_lyrics'], operator ='or'):
	q = {
		"size": 500,
		"explain": True,
		"query": {
			"multi_match": {
				"query": query,
				"fields": fields,
				"operator": operator,
				"type": "best_fields"
			}
		},
		"aggs": {
			"Genre Filter": {
				"terms": {
					"field": "genre.keyword",
					"size": 10
				}
			},
			"Music Filter": {
				"terms": {
					"field": "music.keyword",
					"size": 10
				}
			},
			"Artist Filter": {
				"terms": {
					"field": "artist.keyword",
					"size": 10
				}
			},
			"Lyrics Filter": {
				"terms": {
					"field": "lyrics.keyword",
					"size": 10
				}
			}
		}
	}

	q = json.dumps(q)
	return q

def agg_q():
	q = {
		"size": 0,
		"aggs": {
			"Category Filter": {
				"terms": {
					"field": "genre",
					"size": 10
				}
			}
		}
	}

	return q

def agg_multi_match_and_sort_q(query, sort_num, fields=['title','song_lyrics'], operator ='or'):
	print ('sort num is ',sort_num)
	q = {
		"size": sort_num,
		"sort": [
			{"views": {"order": "desc"}},
		],
		"query": {
			"multi_match": {
				"query": query,
				"fields": fields,
				"operator": operator,
				"type": "best_fields"
			}
		},
		"aggs": {
			"Genre Filter": {
				"terms": {
					"field": "genre.keyword",
					"size": 10
				}
			},
			"Music Filter": {
				"terms": {
					"field": "music.keyword",
					"size": 10
				}
			},
			"Artist Filter": {
				"terms": {
					"field": "artist.keyword",
					"size": 10
				}
			},
			"Lyrics Filter": {
				"terms": {
					"field": "lyrics.keyword",
					"size": 10
				}
			}
		}
	}
	q = json.dumps(q)
	return q


# "Price Filter": {
# 	"range": {
# 		"field": "price",
# 		"ranges": [
# 			{
# 				"from": 0,
# 				"to": 1000
# 			},
# 			{
# 				"from": 1000,
# 				"to": 2000
# 			},
# 			{
# 				"from": 2000,
# 				"to": 3000
# 			}
# 		]
# 	}
# }