import cherrypy
import sqlite3
import os

def db_request(query):
    data_base = os.environ['db_name']
    con = sqlite3.connect(data_base)
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    result = ','.join(map(str, [i for i in cur.fetchall()]))
    con.close()
    return result

class Router(object):
    def __init__(self):
        self.albums = Album()
        self.song = Song()
        self.band = Band()
        self.everyone = Everyone()
        self.search = Search()

    def _cp_dispatch(self, vpath):
        if len(vpath) == 0:  # /
            return self.everyone

        elif len(vpath) == 1:  # /search
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
                cherrypy.request.params['name'] = vpath.pop(0)  # /song name/
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
	                    artist.artist_name, album.album_name, album.album_id
                    FROM track_list
                    JOIN artist on track_list.artist_id = artist.id_artist
                    JOIN album on track_list.album_id = album.album_id
                    WHERE artist.artist_name = "{name}"'''
        result = db_request(query)
        return result


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
 AND artist.artist_name = "{artist}"
        '''
        result = db_request(query)
        return result


class Song(object):
    @cherrypy.expose
    def index(self, artist, name):
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
WHERE song.song_name = "{name}" AND artist_name="{artist}"'''
        result = db_request(query)
        return result


class Everyone(object):
    @cherrypy.expose
    def index(self):
        return


class Search(object):
    @cherrypy.expose
    def index(self):
        pass

if __name__ == '__main__':
    cherrypy.quickstart(Router())

