from pymongo import MongoClient

MONGO_URI = "mongodb+srv://amish:AmishPassword123@cluster0.ivayay0.mongodb.net/MediLinkDB?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['MediLinkDB']
