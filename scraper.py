from bs4 import BeautifulSoup
import requests,time,os
import json,re
import mtranslate

global_song = ''

def get_all_song_url(pg_no):
	url = 'https://sinhalasongbook.com/all-sinhala-song-lyrics-and-chords/?_page={}/'.format(pg_no)
	print(url)
	return url

def get_song_url(line_num):
	with open('song_links.csv', 'r') as f:
		lines = f.readlines()
	return lines[line_num]

def make_req(url):
	# Set headers
	headers = requests.utils.default_headers()
	res = requests.get(url, headers)
	return res.text

def parse_html(html_pg):
	links = []
	soup = BeautifulSoup(html_pg, 'html.parser')
	song_links = soup.find_all("a", {"class": "_blank"})
	for tag in song_links:
		link = tag.get('href')
		links.append(link)
	return links


def process_content(key_val_pair):
	if key_val_pair:
		key_val_pair = key_val_pair.get_text()
		split_pair=key_val_pair.split(':')
		if len(split_pair)>1:
			key = split_pair[0]
			val = split_pair[1]
			if ',' in val:
				values = []
				split_val = val.split(',')
				for value in split_val:
					values.append(value)
				return key,values
			else:
				return key,val
		else:
			return None,None
	else:
		return None,None

def parse_lyrics(lyrics):
	space_set = set([' '])
	processed = ''
	regex = r"([A-z])+|[0-9]|\||-|∆|([.!?\\\/\(\)\+#&])+"
	lyric_lines = lyrics.split('\n')
	for line in lyric_lines:
		new = re.sub(regex, '', line)
		chars = set(new)
		if not ((chars == space_set) or (len(chars) is 0)):
			processed += new + '\n'
	return processed


def parse_html_song(html_pg):
	soup = BeautifulSoup(html_pg, 'html.parser')
	song = {}
	class_list = ["entry-tags","entry-categories","entry-author-name","lyrics","music"]
	title = soup.find('h1', {"class": "entry-title"}).get_text()
	guit_key=soup.find_all('h3', {'class': None})[0].get_text().split('|')
	views = soup.find('div',{'class':'tptn_counter'}).get_text().split()[1].split('Visits')[0]
	if guit_key and len(guit_key)==2:
		guitar_key = guit_key[0].split(':')
		if len(guitar_key)==2:
			guitar_key = guitar_key[1].strip()
			song.update({'guitar_key': guitar_key})
		beat = guit_key[1].split(':')
		if len(beat)==2:
			beat = beat[1].strip()
			song.update({'beat': beat})
	song.update({'title': title})
	song.update({'views': int(views.replace(',',''))})
	for class_l in class_list:
		content = soup.find_all('span',{"class":class_l})
		if content:
			key, val = process_content(content[0])
			if ((not key is None) and (not val is None)):
				song.update({key:val})
		else:
			pass
	unprocessed_lyrics = soup.select('pre')[0].get_text()
	processed_lyrics = parse_lyrics(unprocessed_lyrics)
	song.update({'song_lyrics': processed_lyrics})
	print(song)
	print (processed_lyrics)
	return song

def write_res(links_array):
	with open('song_links.csv','a') as f:
		for link in links_array:
			f.write(link + os.linesep)


def get_song_list():
	for pg_no in range(1, 11):
		url = get_all_song_url(pg_no)
		print ('Scraping the URL : ',url)
		html_pg = make_req(url)
		links_array = parse_html(html_pg)
		write_res(links_array)
		time.sleep(10)

def write_song(song,id):
	with open ('new-corpus/song_' + str(id)+'.json','w+') as f:
		f.write(json.dumps(song))


def scrape_songs():
	with open ('next_song_link.txt', 'r') as f:
		next_index = int(f.readlines()[0])
	while next_index < 500 :
		print('Scraping song',next_index)
		url = get_song_url(int(next_index))
		html_doc = make_req(url)
		song = parse_html_song(html_doc)
		write_song(song,next_index)
		# Scrape song and write to file
		next_index = next_index + 1
		with open('next_song_link.txt', 'w') as f:
			f.write(str(next_index))
		time.sleep (5)

def translate_tag(value_array,global_val_dict):
	if value_array:
		translated_value_array = []
		if type(value_array) == list:
			for english_val in value_array:
				english_val = english_val.strip()
				if english_val in global_val_dict:
					sinhala_gen = global_val_dict[english_val]
				else:
					sinhala_gen = mtranslate.translate(english_val, 'si', 'en')
					global_val_dict.update({english_val: sinhala_gen})
				translated_value_array.append(sinhala_gen)
			return translated_value_array, global_val_dict
		else:
			english_val = value_array.strip()
			if english_val in global_val_dict:
				sinhala_gen = global_val_dict[english_val]
			else:
				sinhala_gen = mtranslate.translate(english_val, 'si', 'en')
				global_val_dict.update({english_val: sinhala_gen})
			translated_value_array.append(sinhala_gen)
			return translated_value_array[0], global_val_dict
	else:
		return None,global_val_dict


def translate():
	# Keep guitar_key,views,song_lyrics,title intact
	# Translate genre,artist,lyricist, music
	# all_songs = []
	# all_genres = {}
	# all_artists = {}
	# all_lyricists = {}
	# all_music = {}

	with open('summary-corpus1/all_songs.json', 'r') as t:
		all_songs = json.loads(t.read())
	with open('summary-corpus1/all_genres.json', 'r') as t:
		all_genres = json.loads(t.read())
	with open('summary-corpus1/all_artists.json', 'r') as t:
		all_artists = json.loads(t.read())
	with open('summary-corpus1/all_lyricists.json', 'r') as t:
		all_lyricists = json.loads(t.read())
	with open('summary-corpus1/all_music.json', 'r') as t:
		all_music = json.loads(t.read())

	for i in range(0,500):
		if i%10==0:
			time.sleep(15)
		with open('new-corpus/song_' + str(i) + '.json', 'r') as f:
			sinhala_song = {}
			song = json.loads(f.read())

		guitar_key = song.get("guitar_key", None)
		title = song.get("title", None)
		artist = song.get("Artist", None)
		genre = song.get("Genre", None)
		lyricist = song.get("Lyrics", None)
		music = song.get("Music", None)
		lyrics = song.get("song_lyrics", None)
		views = song.get('views',None)

		sinhala_song.update({"guitar_key": guitar_key})
		sinhala_song.update({"title": title})
		sinhala_song.update({"song_lyrics": lyrics})
		sinhala_song.update({"views": views})

		sinhala_song.update({"english_lyricst": lyricist})
		sinhala_song.update({"english_music": music})
		sinhala_song.update({"english_artist": artist})

		translated_genre, all_genres = translate_tag(genre, all_genres)
		if translated_genre:
			sinhala_song.update({"Genre": translated_genre})
		time.sleep(2)
		translated_artist, all_artists = translate_tag(artist, all_artists)
		if translated_artist:
			sinhala_song.update({"Artist":translated_artist})
		time.sleep(2)
		translated_lyricist, all_lyricists = translate_tag(lyricist, all_lyricists)
		if translated_lyricist:
			sinhala_song.update({"Lyrics": translated_lyricist})
		time.sleep(2)
		translated_music, all_music = translate_tag(music, all_music)
		if translated_music:
			sinhala_song.update({"Music": translated_music})



		all_songs.append(sinhala_song)
		with open('summary-corpus1/all_songs.json', 'w') as t:
			t.write(json.dumps(all_songs))
		with open('summary-corpus1/all_genres.json', 'w') as t:
			t.write(json.dumps(all_genres))
		with open('summary-corpus1/all_artists.json', 'w') as t:
			t.write(json.dumps(all_artists))
		with open('summary-corpus1/all_lyricists.json', 'w') as t:
			t.write(json.dumps(all_lyricists))
		with open('summary-corpus1/all_music.json', 'w') as t:
			t.write(json.dumps(all_music))

		with open('translated-corpus1/song_' + str(i) + '.json', 'w') as t:
			t.write(json.dumps(sinhala_song))

	print (all_genres)
	print(all_artists)
	print(all_lyricists)
	print(all_music)

if __name__ == "__main__":
	#get_song_list()
	#scrape_songs()
	#translate()
	pass
