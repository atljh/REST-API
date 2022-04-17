import os
import sqlite3
from dotenv import load_dotenv
from googletrans import Translator

translator = Translator()


def db_connect():
    data_base = os.environ.get('DB_NAME')
    conn = sqlite3.connect(data_base)
    # conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return cur, conn


def translate(song_text, translate_to):
    translated_text = translator.translate(song_text, dest=translate_to).text
    return translated_text


def search(search_string):
    cur, conn = db_connect()
    search_dict = {
        'artist': cur.execute(
            "SELECT artist_name FROM artist WHERE artist_name LIKE '%" + search_string + "%'").fetchall(),
        'album': cur.execute("SELECT album_name FROM album WHERE album_name LIKE '%" + search_string + "%'").fetchall(),
        'song': cur.execute("SELECT song_name FROM song WHERE song_name LIKE '%" + search_string + "%'").fetchall()
    }
    conn.close()
    print(search_dict)
    return search_dict


# cur.execute("select * from lang where first_appeared=:year", {"year": 1972})


def get_artist(artist_name):
    cur, conn = db_connect()
    artist_data = cur.execute('''
                    select DISTINCT
                    artist.artist_name, album.album_name
                    FROM track_list
                    JOIN artist on track_list.artist_id = artist.artist_id
                    JOIN album on track_list.album_id = album.album_id
                    WHERE artist.artist_name =:artist_name''',
                              {"artist_name": artist_name}).fetchall()
    conn.close()
    artist_data = [row for row in artist_data[0]]
    return artist_data


def get_album(artist_name, album_name):
    cur, conn = db_connect()
    album_data = cur.execute('''
                    SELECT track_list.track_num, song.song_name,
                         song.song_year,
                         artist.artist_name,    
                         album.album_name,
                         album.album_year,
                         album.album_info
                    FROM track_list
                    JOIN song on track_list.song_id = song.song_id
                    JOIN album on track_list.album_id = album.album_id
                    JOIN artist on track_list.artist_id = artist.artist_id  
                    WHERE album.album_name=:album_name
                    AND artist.artist_name=:artist_name''',
                             {"album_name": album_name, "artist_name": artist_name}).fetchall()
    conn.close()
    album_data = [row for row in album_data[0]]
    return album_data


def get_song(artist_name, song_name, translate_to):
    cur, conn = db_connect()
    # song_data = cur.execute(f'''SELECT song.song_id, artist.artist_id FROM track_list JOIN artist ON track_list.artist_id = artist.artist_id
    #  JOIN song ON track_list.song_id = song.song_id WHERE song.song_name="{song_name}" and artist.artist_name = "{artist_name}" ''').fetchall()
    song_data = cur.execute('''
                    SELECT track_list.track_num,
                        song.song_name,
                        song.song_year,
                        song.song_text,
                        song. origin_lang,
                        artist.artist_name,
                        album.album_name
                    FROM track_list
                    JOIN artist on track_list.artist_id = artist.artist_id
                    JOIN song on track_list.song_id = song.song_id
                    JOIN album on track_list.album_id = album.album_id
                    WHERE song.song_name=:song_name AND artist_name=:artist_name''',
                            {"artist_name": artist_name, "song_name": song_name}).fetchall()

    conn.close()
    song_data = [row for row in song_data[0]]
    translated_text = translate(song_data[3], translate_to)
    song_data.append(translated_text)
    return song_data


def add_to_tracklist(song_id, artist_id, album_id, track_num):
    cur, conn = db_connect()
    cur.execute('''INSERT
                   INTO track_list
                   (song_id, artist_id, album_id, track_num)
                   VALUES
                   (?, ?, ?, ?)''',
                (song_id, artist_id, album_id, int(track_num)))
    conn.commit()
    conn.close()


# cur.execute("insert into lang values (?, ?)", ("C", 1972))


def insert_song(song_data):
    cur, conn = db_connect()
    song_exist = cur.execute('''
                SELECT song.song_id
                FROM song
                WHERE
                song.song_name =:song_name AND song.song_text =:song_text''',
                             {'song_name': song_data['song_name'], 'song_text': song_data['song_text']}).fetchone()
    id_song = None
    if not song_exist:
        cur.execute('''
                INSERT 
                INTO song 
                (song_name, song_text, song_year, origin_lang) 
                VALUES 
                (?, ?, ?, ?)''',
                    (song_data['song_name'], song_data['song_text'], song_data['song_year'], song_data['origin_lang']))
        conn.commit()
        id_song = cur.execute('''
                SELECT song.song_id
                FROM song
                WHERE song.song_name =:song_name''',
                              {'song_name': song_data['song_name']}).fetchone()
        return id_song[0]
    else:
        pass
    conn.close()
    return id_song


def smart_insert_artist(artist_data):
    cur, conn = db_connect()
    id_artist = cur.execute('''
                SELECT artist.artist_id
                FROM artist
                WHERE artist.artist_name =:artist_name''',
                            {'artist_name': artist_data['artist_name']}).fetchone()
    if not id_artist:
        cur.execute('''
                INSERT
                INTO artist
                (artist_name, artist_info) 
                VALUES
                (?, ?)''',
                    (artist_data['artist_name'], artist_data['artist_info']))
        conn.commit()
        id_artist = cur.execute('''
                SELECT artist.artist_id
                FROM artist
                WHERE artist.artist_name =:artist_name''',
                                {'artist_name': artist_data['artist_name']}).fetchone()[0]
    conn.close()
    return id_artist


def smart_insert_album(album_data):
    cur, conn = db_connect()
    id_album = cur.execute('''
                SELECT album.album_id 
                FROM album
                WHERE album.album_name =:album_name''',
                           {'album_name': album_data['album_name']}).fetchone()
    if not id_album:
        cur.execute('''
                INSERT INTO album (album_name, album_year, album_info)
                VALUES
                (?, ?, ?)''',
                    (album_data['album_name'], album_data['album_year'], album_data['album_info']))
        conn.commit()
        id_album = cur.execute('''
                SELECT album.album_id 
                FROM album
                WHERE album.album_name =:album_name''',
                               {'album_name': album_data['album_name']}).fetchone()
    conn.close()
    return id_album[0], album_data['track_num']


def add_song(song_data):
    song_id = insert_song(song_data['song_information'])
    if song_id is None:
        print('song exist')
        return 'Song exist'
    for artist_data in song_data['artist_information']:
        if artist_data.get('artist_name'):
            artist_id = smart_insert_artist(artist_data)
            for album_data in artist_data['album_information']:
                if album_data.get('album_name'):
                    album_id, track_num = smart_insert_album(album_data)
                    add_to_tracklist(song_id, artist_id, album_id, track_num)
        else:
            # add_to_tracklist(song_id, artist_id, None, None)
            pass


def update_song(artist_name, song_name, song_data):
    cur, conn = db_connect()
    song_id = cur.execute('''
                SELECT song.song_id
                FROM track_list
                JOIN artist on track_list.artist_id = artist.artist_id
                JOIN song on track_list.song_id = song.song_id
                WHERE song_name =:song_name AND artist_name=:artist_name''',
                          {'song_name': song_name, 'artist_name': artist_name}).fetchone()[0]
    print('song_id=', song_id)
    cur.execute('''
                UPDATE song
                SET song_name =:song_name, song_text=:song_text, song_year=:song_year, origin_lang=:origin_lang 
                WHERE song_id =:song_id''',
                {'song_name': song_data['song_name'], 'song_text': song_data['song_text'],
                 'song_year': song_data['song_year'], 'origin_lang': song_data['origin_lang'], 'song_id': song_id})

    conn.commit()
    conn.close()


def update_album(artist_name, album_name, album_data):
    cur, conn = db_connect()
    album_id = cur.execute('''
                SELECT album.album_id
                FROM track_list
                JOIN artist on track_list.artist_id = artist.artist_id
                JOIN album on track_list.album_id = album.album_id
                WHERE artist_name =:artist_name AND album_name=:album_name''',
                           {'artist_name': artist_name, 'album_name': album_name}).fetchone()[0]

    cur.execute('''
                UPDATE artist 
                SET album_name =:album_name,
                    album_year =:album_year,
                    album_info =:album_info
                WHERE album_id =:album_id''',
                {'album_name': album_data['album_name'], 'album_info': album_data['artist_info'],
                 'album_year': album_data['album_info'], 'album_id': album_id})
    conn.commit()
    conn.close()


def update_artist(artist_name, artist_data):
    cur, conn = db_connect()
    artist_id = cur.execute('''
                SELECT artist.artist_id
                FROM track_list
                JOIN artist ON track_list.artist_id = artist.artist_id
                WHERE artist_name =:artist_name''',
                            {'artist_name': artist_name}).fetchone()[0]
    cur.execute('''
                UPDATE artist
                SET artist_name =:artist_name,
                    artist_info =: artist_info
                WHERE artist.artist_id =: artist_id''',
                {'artist_name': artist_data['artist_name'], 'artist_info': artist_data['artist_info'],
                 'artist_id': artist_id})
    conn.commit()
    conn.close()


def delete_artist(artist_name):
    cur, conn = db_connect()
    artist_id = cur.execute('''
                SELECT artist.artist_id
                FROM track_list
                JOIN artist ON track_list.artist_id = artist.artist_id
                WHERE artist_name =:artist_name''',
                            {'artist_name': artist_name}).fetchone()[0]

    cur.execute('''
                DELETE
                FROM artist
                WHERE artist.artist_id =:artist_id''', {'artist_id': artist_id})
    conn.commit()
    conn.close()


def delete_album(album_name, artist_name):
    cur, conn = db_connect()
    album_id = cur.execute('''
                SELECT album.album_id
                FROM track_list
                JOIN artist on track_list.artist_id = artist.artist_id
                JOIN album on track_list.album_id = album.album_id
                WHERE artist_name =:artist_name AND album_name=:album_name''',
                           {'artist_name': artist_name, 'album_name': album_name}).fetchone()[0]

    cur.execute('''
                DELETE 
                FROM album
                WHERE album.album_id=:album_id''', {'album_id': album_id})
    conn.commit()
    conn.close()


def delete_song(song_name, artist_name):
    cur, conn = db_connect()
    song_id = cur.execute('''
                SELECT song.song_id
                FROM track_list
                JOIN artist on track_list.artist_id = artist.artist_id
                JOIN song on track_list.song_id = song.song_id
                WHERE song_name =:song_name AND artist_name=:artist_name''',
                          {'song_name': song_name, 'artist_name': artist_name}).fetchone()[0]
    cur.execute('''
                DELETE
                FROM song
                WHERE song.song_id =:song_id''', {'song_id': song_id})
    conn.commit()
    conn.close()
