import shelve
db = shelve.open("shelve-test4.txt")
# db['number'] = [9, 2]
# db['color'] = ['red', 'blue', 'green']
print (db['number'])
print (db['No'])

db.close()
