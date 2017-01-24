import config
import shelve

dictionary = shelve.open(config.shelveName)
words = dictionary.items()
for word in words:
    print (word)
# print (dictionary.items())
