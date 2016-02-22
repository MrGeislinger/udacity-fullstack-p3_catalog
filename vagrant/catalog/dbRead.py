from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog import Base, Category, Item
from random import randint
import datetime
import random


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

def readItems():
    for c in session.query(Item):
      print "%s #%d (Added %s)" %(c.name, c.id, c.date_added)
      print "Category: #%d - %s" %(c.category_id,session.query(Category).filter_by(id=c.category_id).first().name)
      print "Description: \"\n\t%s\"" %c.description
      print "Image: %s\n" %c.image
