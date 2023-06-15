import random
import string

import cherrypy


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """
        <html>
  <head>
    <title>Chat Amigável</title>
    <link rel="stylesheet" href="chat.css">
  </head>
  <body>
    <div id="chatbox"></div>
    <input type="text" id="message">
    <button id="send">Enviar</button>
    <script src="chat.js"></script>
  </body>
</html>
        """

    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))


if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())
