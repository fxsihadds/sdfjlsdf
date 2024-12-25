import pymongo

uri = "mongodb+srv://sihadmiah7:CVrtlv9QKl4mhjCi@telegrambot.unrrxv0.mongodb.net/?retryWrites=true&w=majority&appName=telegrambot"


def connect_db():
    myclient = pymongo.MongoClient(uri)
    mydb = myclient['tgbotusers']
    # Insert a document into a collection to create the database
    mycollection = mydb['users']
    return mycollection