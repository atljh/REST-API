from flask import Flask, request, render_template
import user_data
import os
from models import db


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ.get("DB_NAME")}'
db.init_app(app)


@app.route('/')
def index():
    all_artists = user_data.index()
    return render_template('index.html', **all_artists)


@app.route('/search')
def search():
    if request.method == 'GET':
        request_args = request.args
        search_result = user_data.search(request_args['search_string'])
        return render_template('search_data.html', **search_result)
    else:
        return {}


@app.route('/artist/<artist_name>', methods=['GET', 'PUT', 'DELETE'])
def artist(artist_name):
    if request.method == 'GET':
        artist_data = user_data.get_artist(artist_name)
        return render_template('artist_data.html', **artist_data)
    elif request.method == 'PUT':
        artist_data = request.json
        user_data.update_artist(artist_name, artist_data)
        return f'Artist {artist_name} changed'
    elif request.method == 'DELETE':
        user_data.delete_artist(artist_name)
        return f'Artist {artist_name} deleted'


@app.route('/artist/<artist_name>/album/<album_name>', methods=['GET', 'PUT', 'DELETE'])
def album(artist_name, album_name):
    if request.method == 'GET':
        album_data = user_data.get_album(artist_name, album_name)
        return render_template('album_data.html', **album_data)
    elif request.method == 'PUT':
        album_data = request.json
        user_data.update_album(artist_name, album_name, album_data['artist_information'][0])
        return f'Album {album_name}, {artist_name} changed'
    elif request.method == 'DELETE':
        user_data.delete_song(artist_name, album_name)
        return f'Album {album_name} deleted'


@app.route('/artist/<artist_name>/song/<song_name>', methods=['GET', 'PUT', 'DELETE'])
def song(artist_name, song_name):
    if request.method == 'GET':
        request_args = request.args
        if 'translate_to' in request_args:
            translate_to = request_args.get('translate_to')
        else:
            translate_to = 'ru'
        song_data = user_data.get_song(artist_name, song_name, translate_to)
        return render_template('song_data.html', **song_data)
    elif request.method == 'PUT':
        song_data = request.json
        user_data.update_song(artist_name, song_name, song_data['song_information'])
        return f'Song {song_name}, {artist_name} changed'
    elif request.method == 'DELETE':
        user_data.delete_song(song_name, artist_name)
        return f'Song {song_name} deleted'


@app.route('/add', methods=['POST'])
def add_song():
    if request.method == 'POST':
        user_data.add_song(request.json)
        return request.json
    else:
        return {}


if __name__ == '__main__':
    app.run()
