import cherrypy
from os.path import abspath
from settings import *

class Chat():

    @cherrypy.expose
    def index(self):
        return file('templates/index.html')


if __name__ == '__main__':
    cherrypy.config.update({'server.socker_port': 8082})
    cherrypy.quickstart(Chat(), '/', CONF_INDEX)
