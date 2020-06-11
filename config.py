import os
class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(16)
    MONGO_DBNAME = "Enrollment"
    MONGO_URI = "mongodb+srv://msm98:paras123@cluster0-4gnmc.mongodb.net/Enrollment?retryWrites=true&w=majority"