import config
import telebot
import cherrypy

lucinda = telebot.TeleBot(config.token)

@lucinda.message_handler(content_types=["text"])
def repeat_all_messages(message):
    lucinda.send_message(message.chat.id, message.text)

class Root(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            lucinda.process_new_updates([update])
            return 'POST'
        else:
            return 'GET'
