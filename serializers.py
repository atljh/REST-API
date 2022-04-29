from marshmallow import Schema, fields, validate
import constants


class SongSchema(Schema):
    song_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    song_text = fields.Str(required=False, validate=validate.Length(min=2))
    song_year = fields.Int(required=False, validate=validate.Range(min=1900, max=2500))
    origin_lang = fields.Str(required=False, validate=validate.OneOf(constants.LANG_CODES))


class AlbumSchema(Schema):
    album_name = fields.Str(required=True, validate=validate.Length(min=1))
    album_year = fields.Int(required=False, validate=validate.Range(min=1900, max=2500))
    album_info = fields.Str(required=False, validate=validate.Length(min=1))
    track_num = fields.Int(required=False, validate=validate.Range(min=1, max=100))


class ArtistSchema(Schema):
    artist_name = fields.Str(required=True, validate=validate.Length(min=1))
    artist_info = fields.Str(required=False, validate=validate.Length(min=1))


Song = SongSchema()

Album = AlbumSchema()

Artist = ArtistSchema()