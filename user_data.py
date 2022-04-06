import os
import sqlite3
from dotenv import load_dotenv
from googletrans import Translator

translator = Translator()


def db_request(query):
    data_base = os.environ.get('DB_NAME')
    con = sqlite3.connect(data_base)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    result = [dict(i) for i in cur.fetchall()]
    con.close()
    return result


def translate(song_text, translate_to):
    translated_text = translator.translate(song_text, dest=translate_to).text
    return translated_text


def search(search_string):
    """search_dict = {
                'artist': db_request(f'''SELECT artist_name FROM artist WHERE artist_name LIKE "%{search_string}%"'''),
                'album': db_request(f'''SELECT album_name FROM album WHERE album_name LIKE "%{search_string}%"'''),
                'song': db_request(f'''SELECT song_name FROM song WHERE song_name LIKE "%{search_string}%"''')
            }"""
    search_dict = {}
    for table in ['artist', 'album', 'song']:
        search_dict.update({table: db_request(
            f'''SELECT * FROM "{table}" WHERE "{table}_name" LIKE "%{search_string}%"''')})
    return search_dict


def artist(artist_name):
    query = f'''select DISTINCT
        	                artist.artist_name, album.album_name
                        FROM track_list
                        JOIN artist on track_list.artist_id = artist.id_artist
                        JOIN album on track_list.album_id = album.album_id
                        WHERE artist.artist_name = "{artist_name}"'''
    artist_data = db_request(query)
    return artist_data


def album(artist, album):
    query = f'''SELECT track_list.track_num, song.song_name,
         song.song_year,
    	 artist.artist_name,
    	 album.album_name,
    	 album.album_year,
    	 album.album_info
     FROM track_list
     JOIN song on track_list.song_id = song.song_id
     JOIN album on track_list.album_id = album.album_id
     JOIN artist on track_list.artist_id = artist_id
     WHERE album.album_name = "{album}"
     AND artist.artist_name = "{artist}"'''
    album_data = db_request(query)
    return album_data


def song(artist, song, translate_to):
    query = f'''SELECT DISTINCT track_list.track_num,
    	song.song_name,
    	song.song_year,
    	song.song_text,
    	song. origin_lang,
    	artist.artist_name,
    	album.album_name
    FROM track_list
    JOIN artist on track_list.artist_id = artist_id
    JOIN song on track_list.song_id = song.song_id
    JOIN album on track_list.album_id = album.album_id
    WHERE song.song_name = "{song}" AND artist_name="{artist}"'''
    result = db_request(query)
    translated_text = translate(result[0].get('song_text'), translate_to)
    result[0]['translated'] = translated_text
    song_data = list(result[0].values())
    return song_data
