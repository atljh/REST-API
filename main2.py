import cherrypy
import sqlite3
import os
import json

from googletrans import Translator
# pip install googletrans==3.1.0a0

translator = Translator()


def db_request(query):
    data_base = os.environ['db_name']
    con = sqlite3.connect(data_base)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)
    result = [dict(i) for i in cur.fetchall()]
    con.close()
    return result


def translate(result, translate_to):
    song_text = result[0].get('song_text')
    translated_text = translator.translate(song_text, dest=translate_to).text
    result[0]['translated'] = translated_text
    new_result = list(result[0].values())
    return new_result


class Router(object):
    def __init__(self):
        self.albums = Album()
        self.song = Song()
        self.band = Band()
        self.search = Search()

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:  # /search
            resource_type = vpath.pop(0)
            if resource_type == 'search':
                return self.search
            else:
                return self

        elif len(vpath) == 2:  # /artist/<artist>
            vpath.pop(0)
            cherrypy.request.params['name'] = vpath.pop()
            return self.band

        elif len(vpath) == 4:  # /artist/<artist>/song/<song>
            vpath.pop(0)
            cherrypy.request.params['artist'] = vpath.pop(0)  # artist name
            resource_type = vpath.pop(0)

            if resource_type == 'song':
                cherrypy.request.params['song_name'] = vpath.pop(0)  # /song name/
                return self.song

            elif resource_type == 'album':
                cherrypy.request.params['title'] = vpath.pop(0)  # /album title/
                return self.albums

            else:
                return self
        else:
            vpath = []
            return self

    @cherrypy.expose
    def index(self):
        return 'bad request'


class Band(object):
    @cherrypy.expose
    def index(self, name):
        query = f'''select DISTINCT
    	                artist.artist_name, album.album_name
                    FROM track_list
                    JOIN artist on track_list.artist_id = artist.id_artist
                    JOIN album on track_list.album_id = album.album_id
                    WHERE artist.artist_name = "{name}"'''
        result = db_request(query)
        new_result = list(result[0].values())
        return json.dumps(new_result)


class Album(object):
    @cherrypy.expose
    def index(self, artist, title):
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
 WHERE album.album_name = "{title}"
 AND artist.artist_name = "{artist}"'''
        result = db_request(query)
        new_result = list(result[0].values())
        return json.dumps(new_result)


class Song(object):
    @cherrypy.expose
    def index(self, artist, song_name, translate_to='ru'):
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
WHERE song.song_name = "{song_name}" AND artist_name="{artist}"'''
        result = db_request(query)
        new_result = translate(result, translate_to)
        return json.dumps(new_result, ensure_ascii=False)


class Search(object):
    @cherrypy.expose
    def index(self, search_string):
        """search_dict = {
            'artist': db_request(f'''SELECT artist_name FROM artist WHERE artist_name LIKE "%{search_string}%"'''),
            'album': db_request(f'''SELECT album_name FROM album WHERE album_name LIKE "%{search_string}%"'''),
            'song': db_request(f'''SELECT song_name FROM song WHERE song_name LIKE "%{search_string}%"''')
        }"""
        search_dict = {}
        for table in ['artist', 'album', 'song']:
            search_dict.update({table:  db_request(
                f'''SELECT "{table}_name" FROM "{table}" WHERE "{table}_name" LIKE "%{search_string}%"''')})

        result = []
        for i in search_dict.values():
            for v in i:
                result.append(*v.values())
        return json.dumps(result)


if __name__ == '__main__':
    cherrypy.quickstart(Router())
