from flask import Flask, request
import json
import user_data

app = Flask(__name__)


@app.route('/search')
def search():
    request_args = request.args
    search_result = list(user_data.search(request_args['search_string']).values())
    return json.dumps(search_result)


@app.route('/artist/<artist_name>')
def artist(artist_name: str):
    artist_data = user_data.artist(artist_name)
    return json.dumps(artist_data)


@app.route('/artist/<artist>/album/<album>')
def album(artist, album):
    album_data = user_data.album(artist, album)
    return json.dumps(album_data)


@app.route('/artist/<artist>/song/<song>')
def song(artist, song):
    request_args = request.args
    if 'translate_to' in request_args:
        translate_to = request_args.get('translate_to')
    else:
        translate_to = 'ru'

    song_data = user_data.song(artist, song, translate_to)
    return json.dumps(song_data, ensure_ascii=False)


if __name__ == '__main__':
    app.run()
