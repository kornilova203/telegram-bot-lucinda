import cherrypy
#from app import Root
from datetime import datetime
import bot

app = cherrypy.tree.mount(bot.Root(),'/')

if __name__ == '__main__':
	f = open('mycherry.log','a')
	f.write('wsgi.py __name__ == __main__ (cherrypy.config has changed) ' + str(datetime.now()) + '\n')
	#f.write('hi')
	f.close()
	cherrypy.config.update({
		'log.screen': False,
		'log.access_file': 'cherry.log',
		'log.error_file': 'cherry.err',
		'server.socket_host': '127.0.0.1',
		'server.socket_port': 8080
	})
	#cherrypy.quickstart(bot.Root())
	bot.lucinda.polling(none_stop=True)
