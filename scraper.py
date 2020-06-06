from bs4 import BeautifulSoup
import requests,time,os
import json,re
from lxml import etree

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
	song.update({'song_lyrics':processed_lyrics})
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
	with open ('corpus/song_' + str(id)+'.json','w+') as f:
		f.write(json.dumps(song))


def scrape_songs():
	with open ('next_song_link.txt', 'r') as f:
		next_index = int(f.readlines()[0])
	while next_index < 250 :
		print('Scraping song',next_index)
		url = get_song_url(int(next_index))
		html_doc = make_req(url)
		song = parse_html_song(html_doc)
		write_song(song,next_index)
		# Scrape song and write to file
		next_index = next_index + 1
		with open('next_song_link.txt', 'w') as f:
			f.write(str(next_index))
		time.sleep (15)


if __name__ == "__main__":
	#get_song_list()

	scrape_songs()
