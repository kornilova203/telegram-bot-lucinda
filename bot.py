import config
import telebot
import cherrypy
import shelve

lucinda = telebot.TeleBot(config.token)

usersWhoAddWords = []


def addUserWhoAddsWords(uid):
    if uid in usersWhoAddWords:
        return
    else:
        usersWhoAddWords.append(uid)


def checkIfUserAddsWords(uid):
    if uid in usersWhoAddWords:
        return 1
    else:
        return 0


def deleteUserWhoAddsWords(uid):
    usersWhoAddWords.remove(uid)


@lucinda.message_handler(commands=['start'])
def startCommand(message):
    lucinda.send_message(message.chat.id, "Hello! I will help you to learn "
                            "english words. "
                            "Type /help to see what I can do")


@lucinda.message_handler(commands=['help'])
def helpCommand(message):
    lucinda.send_message(message.chat.id, "To start learning you should "
                            "add words to your dictionary by typing /addwords.\n"
                            "To see your dictionary type /printdict (there you can delete words).\n"
                            "If you want to start learning, type /startlearning. "
                            "I will give you words in english and you should type their translation.")


@lucinda.message_handler(commands=["addwords"])
def addWordsCommand(message):
    cid = message.chat.id
    lucinda.send_message(cid, "Send me words in this format:\n"
                            "english word 1 - translation 1\nenglish word 2 - translation 2")
    addUserWhoAddsWords(cid)


@lucinda.message_handler(func=lambda message: checkIfUserAddsWords(message.chat.id) == 1)
def addWordsToDictionary(message):
    cid = message.chat.id
    text = message.text
    text = text.replace(" ", "")
    text = text.lower()
    if addWordsFromText(cid, text):
        lucinda.send_message(cid, "success!")
    else:
        lucinda.send_message(cid, "Sorry, I cant understand your message. Don't forget to put\'-\' betweent word and trandlation. Please try again /addwords");
    deleteUserWhoAddsWords(cid)


# Add words from text message
# Input parameters:
def addWordsFromText(cid, text):
    dictionary = shelve.open(config.shelveName)
    try:  # try to get dict from shelve
        userDict = dictionary[str(cid)]
    except:  # if there is no dict for this user
        userDict = {} # dictionary  # create new dict
    lines = text.split('\n')
    for line in lines:
        try:
            word, translation = line.split('-')
        except:
            dictionary.close()
            return 0
        if translation == "":
            dictionary.close()
            return 0
        lucinda.send_message(cid, word + " - " + translation + "\n")
        userDict[word] = translation
    dictionary[str(cid)] = userDict  # add word to dictionary
    dictionary.close()
    return 1


@lucinda.message_handler(commands=['printdict'])
def printDict(message):
    cid = message.chat.id
    dictionary = shelve.open(config.shelveName)
    try:
        userDict = dictionary[str(cid)]
    except:
        lucinda.send_message(cid, "Your dictionary is empty")
        return
    response = ""
    for entry in userDict:
        response = response + entry + ' - ' + userDict[entry] + '\n'
    dictionary.close()
    lucinda.send_message(cid, response)


@lucinda.message_handler(content_types=["text"])
def textMessages(message):
    lucinda.send_message(message.chat.id, "Sorry, I cannot understand what you said. "
                            "Type /help to see what I can do")


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
