import sqlite3
from googletrans import Translator
from models import artist as artist_model, song as song_model, album as album_model, track_list as track_list_model
from models import delete_smth, create_smth, commit_me
from models import db
from serializers import Song, Album, Artist


translator = Translator()


def translate(song_text, translate_to):
    translated_text = translator.translate(song_text, dest=translate_to).text
    return translated_text


def index():
    all_artists = artist_model.query.add_columns(artist_model.artist_name).all()
    all_artists = [dict(itm) for itm in all_artists]
    all_artist_dict = {'artist_list': all_artists}
    return all_artist_dict


def search(search_string):
    result_song = song_model.query.join(track_list_model, track_list_model.song_id == song_model.song_id) \
        .join(artist_model, artist_model.artist_id == track_list_model.artist_id) \
        .add_columns(artist_model.artist_name, song_model.song_name) \
        .filter(song_model.song_name.like(f'%{search_string}%')).all()
    result_album = album_model.query \
        .join(track_list_model, track_list_model.album_id == album_model.album_id) \
        .join(artist_model, track_list_model.artist_id == artist_model.artist_id) \
        .add_columns(artist_model.artist_name, album_model.album_name) \
        .filter(album_model.album_name.like(f'%{search_string}%')).all()
    result_artist = artist_model.query \
        .add_columns(artist_model.artist_name) \
        .filter(artist_model.artist_name.like(f'%{search_string}%')).all()
    search_result = {
                    'song': [dict(itm) for itm in result_song],
                    'album': [dict(itm) for itm in result_album],
                    'artist': [dict(itm) for itm in result_artist]
                     }
    search_dict = {'song_list': search_result['song'], 'album_list': search_result['album'], 'artist_list': search_result['artist']}
    return search_dict


def get_artist(artist_name):
    artist_data = artist_model.query.join(track_list_model, track_list_model.artist_id == artist_model.artist_id) \
        .join(album_model, track_list_model.album_id == album_model.album_id) \
        .add_columns(artist_model.artist_name, album_model.album_name) \
        .filter(artist_model.artist_name == artist_name).all()
    artist_data = [dict(itm) for itm in artist_data]
    artist_dict = {'album_list': artist_data, 'artist_name': artist_name}
    return artist_dict


def get_album(artist_name, album_name):
    album_data = album_model.query.join(track_list_model, track_list_model.album_id == album_model.album_id) \
        .join(song_model, track_list_model.song_id == song_model.song_id) \
        .join(artist_model, track_list_model.artist_id == artist_model.artist_id) \
        .add_columns(track_list_model.track_num, song_model.song_name, artist_model.artist_name, album_model.album_name, album_model.album_year,
                     album_model.album_info) \
        .filter(album_model.album_name == album_name) \
        .filter(artist_model.artist_name == artist_name).all()
    album_data = [dict(itm) for itm in album_data]
    album_dict = {'songs_list': album_data, 'artist_name': artist_name, 'album_name': album_name,
            'album_info': album_data[0]['album_info'], 'track_num': album_data[0]['track_num']}
    return album_dict


def get_song(artist_name, song_name, translate_to):
    song_data = song_model.query.join(track_list_model, track_list_model.song_id == song_model.song_id) \
        .join(artist_model, track_list_model.artist_id == artist_model.artist_id) \
        .join(album_model, track_list_model.album_id == album_model.album_id) \
        .add_columns(song_model.song_name, song_model.song_year, song_model.song_text, song_model.origin_lang,
                     artist_model.artist_name, album_model.album_name) \
        .filter(song_model.song_name == song_name) \
        .filter(artist_model.artist_name == artist_name).all()
    song_data = [dict(itm) for itm in song_data]
    song_dict = {'artist_name': artist_name, 'album_name': song_data[0]['album_name'], 'song_name': song_name,
            'song_text': song_data[0]['song_text'], 'song_year': song_data[0]['song_year'],
            'origin_lang': song_data[0]['origin_lang']}
    translated_text = translate(song_data[0]['song_text'], translate_to)
    song_dict.update({'translated_text': translated_text})
    return song_dict


def add_to_tracklist(song_id, artist_id, album_id, track_num):
    track_list = track_list_model(song_id=song_id, artist_id=artist_id, album_id=album_id, track_num=track_num)
    create_smth(track_list)


def insert_song(song_data):
    song_query = song_model.query \
        .add_columns(song_model.song_id) \
        .filter(song_model.song_name == song_data['song_name']) \
        .filter(song_model.song_text == song_data['song_text']).first()
    song_id = None
    if not song_query:
        errors = Song.validate(song_data)
        if errors:
            print(errors)
            return errors
        song = song_model(song_name=song_data['song_name'], song_text=song_data['song_text'],
                              song_year=song_data['song_year'], origin_lang=song_data['origin_lang'])
        create_smth(song)
        song_id = song.song_id
    else:
        pass
    return song_id


def insert_artist(artist_data):
    artist_query = artist_model.query \
        .add_columns(artist_model.artist_id) \
        .filter(artist_model.artist_name == artist_data['artist_name']) \
        .filter(artist_model.artist_info == artist_data['artist_info']).first()
    artist_id = None
    if not artist_query:
        errors = Artist.validate({'artist_info': artist_data.get('artist_info'), 'artist_name': artist_data.get('artist_name')})
        if errors:
            print(errors)
            return errors
        artist = artist_model(artist_name=artist_data['artist_name'], artist_info=artist_data['artist_info'])
        create_smth(artist)
        artist_id = artist.artist_id
    else:
        pass
    return artist_id


def insert_album(album_data):
    album_query = album_model.query \
        .add_columns(album_model.album_id) \
        .filter(album_model.album_name == album_data['album_name']) \
        .filter(album_model.album_info == album_data['album_info']).first()
    album_id = None
    track_num = None
    if not album_query:
        errors = Album.validate(album_data)
        if errors:
            print('alb_errors', errors)
            return errors
        album = album_model(album_name=album_data['album_name'], album_year=album_data['album_year'],
                            album_info=album_data['album_info'])
        create_smth(album)
        album_id = album.album_id
        track_num = album_data['track_num']
    else:
        pass
    print(album_id, track_num)
    return album_id, track_num


def add_song(song_data):
    song_id = insert_song(song_data['song_information'])
    if song_id is None:
        print('song exist')
        return 'Song exist'
    for artist_data in song_data['artist_information']:
        if artist_data.get('artist_name'):
            artist_id = insert_artist(artist_data)
            for album_data in artist_data['album_information']:
                if album_data.get('album_name'):
                    album_id, track_num = insert_album(album_data)
                    add_to_tracklist(song_id, artist_id, album_id, track_num)
        else:
            # add_to_tracklist(song_id, artist_id, None, None)
            pass


def update_song(artist_name, song_name, song_data):
    errors = Song.validate(song_data)
    if errors:
        return errors
    song_query = song_model.query.join(track_list_model, track_list_model.song_id == song_model.song_id) \
        .join(artist_model, artist_model.artist_id == track_list_model.artist_id).add_columns(song_model.song_id) \
        .filter(artist_model.artist_name == artist_name)\
        .filter(song_model.song_name == song_name).first()
    song_id = song_query.song_id
    song = song_model.query.get(song_id)
    song.song_name = song_data['song_name']
    song.song_text = song_data['song_text']
    song.song_year = song_data['song_year']
    song.origin_lang = song_data['origin_lang']
    db.session.commit()


def update_album(artist_name, album_name, album_data):
    errors = Album.validate(album_data)
    if errors:
        return errors
    album_query = album_model.query.join(track_list_model,track_list_model.album_id == album_model.album_id) \
        .join(artist_model, artist_model.artist_id == track_list_model.artist_id).add_columns(album_model.album_id) \
        .filter(artist_model.artist_name == artist_name) \
        .filter(album_model.album_name == album_name).first()
    album_id = album_query.album_id
    album = album_model.query.get(album_id)
    album.album_name = album_data['album_name']
    album.album_year = album_data['album_year']
    album.album_info = album_data['album_info']
    db.session.commit()


def update_artist(artist_name, artist_data):
    errors = Artist.validate(artist_data)
    if errors:
        return errors
    artist_query = artist_model.query.add_columns(artist_model.artist_id) \
        .filter(artist_model.artist_name == artist_name).first()
    artist = artist_model.query.get(artist_query.artist_id)
    artist.artist_name = artist_data['artist_name']
    artist.artist_info = artist_data['artist_info']
    db.session.commit()


def delete_artist(artist_name):
    artist_query = artist_model.query.join(track_list_model, track_list_model.artist_id == artist_model.artist_id) \
                .join(album_model, album_model.album_id == track_list_model.album_id) \
                .join(song_model, song_model.song_id == track_list_model.song_id) \
                .add_columns(artist_model.artist_id, album_model.album_id, song_model.song_id) \
                .fliter(artist_model.artist_name == artist_name).first()
    artist_id = artist_query.artist_id
    album_id = artist_query.album_id
    song_id = artist_query.song_id
    artist = artist_model.get(artist_id)
    album = album_model.get(album_id)
    song = song_model.get(song_id)
    track_list = track_list_model.get(artist_id)
    print(track_list)
    delete_smth(artist)
    delete_smth(album)
    delete_smth(song)


def delete_album(album_name, artist_name):
    album_query = album_model.query.join(track_list_model, track_list_model.album_id == album_model.album_id) \
                .join(artist_model, artist_model.artist_id == track_list_model.artist_id) \
                .add_columns(album_model.album_id) \
                .filter(artist_model.artist_name == artist_name) \
                .filter(album_model.album_name == album_name).first()
    album_id = album_query.album_id
    album = album_model.get(album_id)
    delete_smth(album)


def delete_song(song_name, artist_name):
    song_query = song_model.query.join(track_list_model, track_list_model.song_id == song_model.song_id) \
                .join(artist_model, artist_model.artist_id == track_list_model.artist_id)\
                .add_columns(song_model.song_id) \
                .filter(artist_model.artist_name == artist_name) \
                .filter(song_model.song_name == song_name).first()
    song_id = song_query.song_id
    song = song_model.query.get(song_id)
    delete_smth(  song)
