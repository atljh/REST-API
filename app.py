from flask import Flask, request
import json
import user_data

app = Flask(__name__)


@app.route('/search')
def search():
    request_args = request.args
    search_result = list(user_data.search(request_args['search_string']).values())
    return json.dumps(search_result)


@app.route('/artist/<artist_name>', methods=['GET', 'PUT', 'DELETE'])
def artist(artist_name):
    if request.method == 'GET':
        artist_data = user_data.get_artist(artist_name)
        return json.dumps(artist_data)
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
        return json.dumps(album_data)
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
        return json.dumps(song_data, ensure_ascii=False)
    elif request.method == 'PUT':
        song_data = request.json
        user_data.update_song(artist_name, song_name, song_data['song_information'])
        return f'Song {song_name}, {artist_name} changed'
    elif request.method == 'DELETE':
        user_data.delete_song(song_name, artist_name)
        return f'Song {song_name} deleted'


@app.route('/add', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        user_data.add_song(request.json)
        return request.json
    else:
        return {}


if __name__ == '__main__':
    app.run()
