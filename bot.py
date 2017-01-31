import config
import telebot
import cherrypy
import shelve
# import requests
import random


lucinda = telebot.TeleBot(config.token)

usersWhoAddWords = []
usersWhoDeleteWords = []
usersWhoLearnWords = {}


# functions for checking if person adding words
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


# check if person is deleting words
def addUserWhoDeletesWords(uid):
    if uid in usersWhoDeleteWords:
        return
    else:
        usersWhoDeleteWords.append(uid)


def checkIfUserDeletesWords(uid):
    if uid in usersWhoDeleteWords:
        return 1
    else:
        return 0


def deleteUserWhoDeletesWords(uid):
    usersWhoDeleteWords.remove(uid)


# check if person is learning words
def addUserWhoLearnsWords(uid):
    if uid in usersWhoLearnWords:
        return
    else:
        usersWhoLearnWords[uid] = ""


def checkIfUserLearnsWords(uid):
    if uid in usersWhoLearnWords:
        return 1
    else:
        return 0


def deleteUserWhoLearnsWords(uid):
    usersWhoLearnWords.pop(uid)


@lucinda.message_handler(commands=['start'])
def startCommand(message):
    lucinda.send_message(message.chat.id, "Hello! I will help you to learn "
                        "english words. "
                        "Type /help to see what I can do")


@lucinda.message_handler(commands=['help'])
def helpCommand(message):
    lucinda.send_message(message.chat.id, "To start learning you should "
                        "add words to your dictionary by typing /addwords.\n"
                        "To see your dictionary type /printdict "
                        "(there you can delete words).\n"
                        "If you want to start learning, type /startlearning. "
                        "I will give you words in english and you should type their translation.")


@lucinda.message_handler(commands=['stop'])
def stopCommand(message):
    cid = message.chat.id
    # lucinda.send_message(cid, "stop")
    if checkIfUserLearnsWords(cid) == 1:
        deleteUserWhoLearnsWords(cid)
        lucinda.send_message(cid, "Learning was stopped")
    if checkIfUserAddsWords(cid) == 1:
        deleteUserWhoAddsWords(cid)
        lucinda.send_message(cid, "Adding words was stopped")
    if checkIfUserDeletesWords(cid) == 1:
        deleteUserWhoDeletesWords(cid)
        lucinda.send_message(cid, "Deleting words was stopped")


@lucinda.message_handler(commands=["addwords"])
def addWordsCommand(message):
    cid = message.chat.id
    lucinda.send_message(cid, "Send me words in this format:\n"
                            "english word 1 - translation 1\nenglish word 2 - translation 2\n"
                            "To stop command type /stop")
    addUserWhoAddsWords(cid)


@lucinda.message_handler(commands=["deletewords"])
def deleteWordsCommand(message):
    cid = message.chat.id
    dictionary = shelve.open(config.shelveName)
    if ifDictIsEmpty(cid, dictionary) == 1:  # if dict is empty
        lucinda.send_message(cid, "Your dictionary is empty ")
        dictionary.close()
        return
    dictionary.close()
    lucinda.send_message(cid, "Send me words, which you want to delete, in this format:\n"
                            "english word 1, english word 2, english word 3\n"
                            "To stop command type /stop")
    addUserWhoDeletesWords(cid)


@lucinda.message_handler(commands=["startlearning"])
def startlearningCommand(message):
    cid = message.chat.id
    dictionary = shelve.open(config.shelveName)
    if ifDictIsEmpty(cid, dictionary) == 1:  # if dict is empty
        lucinda.send_message(cid, "Your dictionary is empty ")
        dictionary.close()
        return
    dictionary.close()
    lucinda.send_message(cid, "I will send you word, you should type translation\n"
                            "To stop command type /stop")
    addUserWhoLearnsWords(cid)
    sendWord(cid)


# send english word for user
# there is at least one word in dict
def sendWord(cid):
    dictionary = shelve.open(config.shelveName)
    userDict = dictionary[str(cid)]
    # length = len(userDict.keys())
    translation = random.choice(list(userDict.keys()))
    word = userDict[translation]
    if len(userDict.keys()) != 1:
        while word == usersWhoLearnWords[cid]:
            translation = random.choice(list(userDict.keys()))
            word = userDict[translation]
    usersWhoLearnWords[cid] = translation
    lucinda.send_message(cid, word)
    dictionary.close()


@lucinda.message_handler(func=lambda message: checkIfUserAddsWords(message.chat.id) == 1)
def addWordsToDictionary(message):
    cid = message.chat.id
    deleteUserWhoAddsWords(cid)
    text = message.text
    # text = text.replace("\n", "~")
    # requests.post("http://127.0.0.1:4242/processwords", data={'text': str(text)})
    text = text.replace(" ", "")
    text = text.lower()
    if addWordsFromText(cid, text):
        lucinda.send_message(cid, "success!")
    else:
        lucinda.send_message(cid, "Sorry, I cant understand your message. "
                            "Don't forget to put\'-\' betweent word and "
                            "translation. Please try again /addwords")


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


@lucinda.message_handler(func=lambda message: checkIfUserDeletesWords(message.chat.id) == 1)
def deleteWordsFromDictionary(message):
    cid = message.chat.id
    deleteUserWhoDeletesWords(cid)
    text = message.text
    text = text.replace(" ", "")
    text = text.lower()
    deleteWordsFromText(cid, text)


@lucinda.message_handler(func=lambda message: checkIfUserLearnsWords(message.chat.id) == 1)
def checkWord(message):
    cid = message.chat.id
    # deleteUserWhoDeletesWords(cid)
    text = message.text
    text = text.replace(" ", "")
    text = text.lower()
    if text == usersWhoLearnWords[cid]:
        lucinda.send_message(cid, "Right!")
    else:
        lucinda.send_message(cid, "No. It is " + usersWhoLearnWords[cid] +
                                "\nTo stop type /stop")
    sendWord(cid)


def deleteWordsFromText(cid, text):
    dictionary = shelve.open(config.shelveName)
    userDict = dictionary[str(cid)]  # garanteed that it is not empty
    words = text.split(',')
    for word in words:
        try:
            userDict[word]  # check if word is in dict
            userDict.pop(word)
            lucinda.send_message(cid, "Word \"" + word + "\" was deleted")
        except:
            lucinda.send_message(cid, "There is no word \"" + word + "\" in your dictionary")
    dictionary[str(cid)] = userDict  # add new user dict to dictionary
    dictionary.close()


@lucinda.message_handler(commands=['printdict'])
def printDict(message):
    cid = message.chat.id
    dictionary = shelve.open(config.shelveName)
    if ifDictIsEmpty(cid, dictionary) == 1:  # if dict is empty
        lucinda.send_message(cid, "Your dictionary is empty")
        dictionary.close()
        return
    userDict = dictionary[str(cid)]
    response = ""
    for entry in userDict:
        response = response + entry + ' - ' + userDict[entry] + '\n'
    dictionary.close()
    if response == "":
        lucinda.send_message(cid, "Your dictionary is empty")
        return
    lucinda.send_message(cid, response)


@lucinda.message_handler(content_types=["text"])
def textMessages(message):
    lucinda.send_message(message.chat.id, "Sorry, I cannot understand what you said. "
                            "Type /help to see what I can do")


def ifDictIsEmpty(cid, dictionary):
    try:
        userDict = dictionary[str(cid)]
    except:
        return 1
    if len(userDict.keys()) == 0:
        return 1
    else:
        return 0

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

# class ResultProcessWords():
#     @charrypy.expose
#     def index(self):
#         print ("ResultProcessWords GET")
