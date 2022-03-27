import cherrypy


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

        if len(vpath) == 1:  # /search
            resource_type = vpath.pop(0)
            if resource_type == 'search':
                return self.search
            else:
                return 'unknown type'

        if len(vpath) == 2:  # /artist/<artist>
            vpath.pop(0)
            cherrypy.request.params['name'] = vpath.pop()
            return self.band

        if len(vpath) == 4:  # /artist/<artist>/song/<song>
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
                return 'unknown type'

        return vpath


class Band(object):
    @cherrypy.expose
    def index(self, name):
        return  # f'SELECT * FROM {name}'


class Album(object):
    @cherrypy.expose
    def index(self, artist, title):
        return 'About %s by %s...' % (artist, title)


class Song(object):
    @cherrypy.expose
    def index(self, artist, name):
        return 'Song %s by %s...' % (artist, name)


class Everyone(object):
    @cherrypy.expose
    def index(self):
        return  # SELECT * FROM artists


class Search(object):
    @cherrypy.expose
    def index(self):
        pass



if __name__ == '__main__':
    cherrypy.quickstart(Router())
