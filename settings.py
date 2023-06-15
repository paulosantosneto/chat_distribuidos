from os.path import abspath

CONF_INDEX = {
        '/templates': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': abspath('./templates')
            }
        }

