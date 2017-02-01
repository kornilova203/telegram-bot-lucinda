import config
import telebot
import shelve
import requests
import random


lucinda = telebot.TeleBot(config.token)

# lists for ids of users who typed /addwords /deletewords or /startlearning
# it is necessary for understanding that
# user's message was send after typing command
usersWhoAddWords = []
usersWhoDeleteWords = []

# this dict is for keeping word which user is going to guess
usersWhoLearnWords = {}


# Add user to list
# This function is called when user type commands which
#     requires futher message from him
# It is necessary for understanding that
#     user's message was send after typing command
def addUserToList(cid, uList):
    if cid not in uList:
        uList.append(cid)


# Add user to list of people who learns words
# key of list is user id
# value of list is word which user is going to guess
def addUserWhoLearnsWords(uid):
    if uid in usersWhoLearnWords:
        return
    else:
        usersWhoLearnWords[uid] = ""


# responses for commands
commands = {
    "start": "Hello! I will help you to learn english words. "
             "Type /help to see what I can do",
    "help": "To start learning you should "
            "add words to your dictionary by typing /addwords.\n"
            "To see your dictionary type /printdict "
            "(there you can delete words).\n"
            "If you want to start learning, type /startlearning. "
            "I will give you words in english and "
            "you should type their translation.",
    "addwords": "Send me words in this format:\n"
                "english word 1 - translation 1\n"
                "english word 2 - translation 2\n"
                "To stop command type /stop",
    "deletewords": "Send me words, which you want to "
                   "delete, in this format:\nenglish word 1, "
                   "english word 2, english word 3\n"
                   "To stop command type /stop",
    "startlearning": "I will send you word, you should type translation\n"
                     "To stop command type /stop"
}


# function for command /start
@lucinda.message_handler(commands=['start'])
def startCommand(message):
    lucinda.send_message(message.chat.id, commands["start"])


# function for command /help
@lucinda.message_handler(commands=['help'])
def helpCommand(message):
    lucinda.send_message(message.chat.id, commands["help"])


# function for command /stop
# first understand what command is going to be stopped
# then delete person from list
# and send message
@lucinda.message_handler(commands=['stop'])
def stopCommand(message):
    cid = message.chat.id
    if cid in usersWhoLearnWords:
        usersWhoLearnWords.pop(cid)
        lucinda.send_message(cid, "Learning was stopped")
    if cid in usersWhoAddWords:
        usersWhoAddWords.remove(cid)
        lucinda.send_message(cid, "Adding words was stopped")
    if cid in usersWhoDeleteWords:
        usersWhoDeleteWords.remove(cid)
        lucinda.send_message(cid, "Deleting words was stopped")


# function for command /addwords
@lucinda.message_handler(commands=["addwords"])
def addWordsCommand(message):
    cid = message.chat.id
    lucinda.send_message(cid, commands["addwords"])
    addUserToList(cid, usersWhoAddWords)


# Add words from message to user's dict
@lucinda.message_handler(func=lambda message: message.chat.id in usersWhoAddWords)
def addWordsToDictionary(message):
    cid = message.chat.id
    usersWhoAddWords.remove(cid)
    text = message.text
    text = text.replace(" ", "")
    text = text.lower()
    if addWordsFromText(cid, text):
        lucinda.send_message(cid, "success!")
    else:
        lucinda.send_message(cid, "Sorry, I cant understand your message. "
                             "Don't forget to put\'-\' between word and "
                             "translation. Please try again /addwords")


# Add words from text message
# Input parameters:
def addWordsFromText(cid, text):
    dictionary = shelve.open(config.dictName)
    try:  # try to get dict from shelve
        userDict = dictionary[str(cid)]
    except:  # if there is no dict for this user
        userDict = {}  # create new user dict
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
        addExamples(word)
    dictionary[str(cid)] = userDict  # add word to dictionary
    dictionary.close()
    return 1


# add examples of word to "examples" shelve
# if there is no examples, add "no examples"
# 1. try to get entry from "examples"
# 2. if there is no such entry
#   make request
#   if response is correct and has examples
#       add examples to shelve
#   else
#       add "no examples"
def addExamples(word):
    with shelve.open(config.examplesDictName) as examples:
        try:
            examples[word]
        except:  # if there is no entry for this word
            response = requests.get("https://twinword-word-graph-dictionary.p.mashape.com/example/?entry=" +
                                    word, headers=config.headers)
            if (response.status_code == 200 and
                    response.json()['result_msg'] != 'Entry word not found'):
                examples[word] = response.json()["example"]
            else:
                examples[word] = "No examples"


# function for command /deletewords
@lucinda.message_handler(commands=["deletewords"])
def deleteWordsCommand(message):
    cid = message.chat.id
    with shelve.open(config.dictName) as dictionary:  # open shelve
        if ifDictIsEmpty(cid, dictionary):
            lucinda.send_message(cid, "Your dictionary is empty ")
            return
        lucinda.send_message(cid, commands["deletewords"])
        addUserToList(cid, usersWhoDeleteWords)


# function for command /startlearning
@lucinda.message_handler(commands=["startlearning"])
def startlearningCommand(message):
    cid = message.chat.id
    with shelve.open(config.dictName) as dictionary:  # open shelve
        if ifDictIsEmpty(cid, dictionary):
            lucinda.send_message(cid, "Your dictionary is empty. /addwords first")
            return
        lucinda.send_message(cid, commands["startlearning"])
        addUserWhoLearnsWords(cid)
        sendWord(cid)  # send english word to user


# send sentence with english word to user
def sendWord(cid):
    with shelve.open(config.dictName) as dictionary:  # open shelve
        userDict = dictionary[str(cid)]
        word = random.choice(list(userDict.keys()))
        if len(userDict.keys()) != 1:
            while userDict[word] == usersWhoLearnWords[cid]:  # do not send one word twice
                word = random.choice(list(userDict.keys()))
        usersWhoLearnWords[cid] = userDict[word]  # remember translation of word
        example = getExample(word)  # try to get sentence with word
        if example:
            lucinda.send_message(cid, example + "\nTranslate word \"" + word +
                                 "\" in this sentence.")
        else:
            lucinda.send_message(cid, word)


# get sentence with word
def getExample(word):
    with shelve.open(config.examplesDictName) as examples:  # open shelve with examples
        try:
            exampleList = examples[word]
        except:
            return False
        if exampleList == "No examples":
            return False
        else:
            example = random.choice(exampleList)
            return example


# delete words which user send in message
@lucinda.message_handler(func=lambda message: message.chat.id in usersWhoDeleteWords)
def deleteWordsFromDictionary(message):
    cid = message.chat.id
    usersWhoDeleteWords.remove(cid)
    text = message.text
    text = text.replace(" ", "")  # remove spaces
    text = text.lower()
    deleteWordsFromText(cid, text)


# delete words which user send in message
def deleteWordsFromText(cid, text):
    with shelve.open(config.dictName) as dictionary:  # open shelve
        userDict = dictionary[str(cid)]  # garanteed that it is not empty
        words = text.split(',')  # split text into separate words
        for word in words:
            try:
                userDict[word]  # check if word is in dict
                userDict.pop(word)
                lucinda.send_message(cid, "Word \"" + word + "\" was deleted")
            except:
                lucinda.send_message(cid, "There is no word \"" + word +
                                     "\" in your dictionary")
        dictionary[str(cid)] = userDict  # add new user dict to dictionary


# Check user's answer
@lucinda.message_handler(func=lambda message: message.chat.id in usersWhoLearnWords)
def checkWord(message):
    cid = message.chat.id
    text = message.text
    text = text.replace(" ", "")
    text = text.lower()
    if text == usersWhoLearnWords[cid]:  # if user's answer is correnct
        lucinda.send_message(cid, "Right!")
    else:
        lucinda.send_message(cid, "No. It is \"" + usersWhoLearnWords[cid] +
                             "\"\nTo stop type /stop")
    sendWord(cid)  # send new word to user


# Function for command /printdict
@lucinda.message_handler(commands=['printdict'])
def printDict(message):
    cid = message.chat.id
    with shelve.open(config.dictName) as dictionary:  # open shelve
        if ifDictIsEmpty(cid, dictionary):  # if dict is empty
            lucinda.send_message(cid, "Your dictionary is empty")
            return
        userDict = dictionary[str(cid)]
        response = ""
        for entry in userDict:  # add all words to response
            response = response + entry + ' - ' + userDict[entry] + '\n'
        lucinda.send_message(cid, response)


@lucinda.message_handler(content_types=["text"])
def textMessages(message):
    lucinda.send_message(message.chat.id, "Sorry, I cannot understand what "
                         "you said. Type /help to see what I can do")


def ifDictIsEmpty(cid, dictionary):
    try:
        userDict = dictionary[str(cid)]
    except:
        return True
    if len(userDict.keys()) == 0:
        return True
    else:
        return False


lucinda.polling(none_stop=True)
