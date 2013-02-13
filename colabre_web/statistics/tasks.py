import sys
import time
from celery import Celery
from pymongo import MongoClient

celery = Celery('tasks', broker='amqp://guest@localhost//', backend='amqp')

@celery.task
def log(collection_name, obj):
    time.sleep(10)
    connection = MongoClient('127.0.0.1', 27017)
    db = connection.colabre
    db[collection_name].insert(obj)