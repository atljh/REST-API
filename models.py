from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.Text, nullable=False)
    album_year = db.Column(db.Integer, nullable=False)
    album_info = db.Column(db.Text, nullable=True)


class artist(db.Model):
    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.Text, nullable=False)
    artist_info = db.Column(db.Text, nullable=True)


class song(db.Model):
    song_id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.Text, nullable=False)
    song_text = db.Column(db.Text, unique=True, nullable=False)
    song_year = db.Column(db.Integer, nullable=False)
    origin_lang = db.Column(db.Text, nullable=True)


class track_list(db.Model):
    table_id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer)
    album_id = db.Column(db.Integer)
    song_id = db.Column(db.Integer)
    track_num = db.Column(db.Integer)


def commit_me():
    db.session.commit()


def delete_smth(obj_in):
    db.session.delete(obj_in)
    commit_me()


def create_smth(obj_in):
    db.session.add(obj_in)
    commit_me()
