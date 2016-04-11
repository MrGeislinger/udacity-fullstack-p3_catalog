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


#Add Categories
soccer = Category(name = "Soccer")
session.add(soccer)

snowboarding = Category(name = "Snowboarding")
session.add(snowboarding)

hockey = Category(name = "Hockey")
session.add(hockey)

baseball = Category(name = "Baseball")
session.add(baseball)
session.commit()

#Add Items to catalog

items = ['Shinguards','Jersey','Soccer Cleats','Goggles','Snowboard','Stick',\
 'Bat']
categories = [ soccer,soccer,soccer,snowboarding,snowboarding,hockey,baseball]
itemsWithCategories = zip(items,categories):

images = {'Shinguards':"http://ep.yimg.com/ay/yhst-96316601417599/nike-usa-mercurial-lite-shinguards-royal-5.jpg",
'Jersey':"http://image.made-in-china.com/4f0j00JMetfqWlCVog/2012-New-Style-Football-Jersey-Sport-Jersey-Soccer-Shirt.jpg",
'Soccer Cleats':"https://s-media-cache-ak0.pinimg.com/236x/66/0e/61/660e61232c8f3ac243a56ad013087b50.jpg",
'Goggles':"http://www.gooutdoors.co.uk/Lib/Img/ski-goggles.jpg",
'Snowboard':"",
'Stick':"",
'Bat':""
}

def CreateDescription(nameStr,categoryEntry):
    categoryStr = categoryEntry.name
    descriptionStr = "%s: used in the sport of %s" %(nameStr,categoryStr)
    return descriptionStr

def CreateRandomDate():
	today = datetime.date.today()
	days_ago = randint(0,540)
	date = today - datetime.timedelta(days = days_ago)
	return date


for i,c in itemsWithCategories:
    new_item = Item( name = i, category_id = c.id, image=images[i],
     description = CreateDescription(i,c), date_added = CreateRandomDate() )
    session.add(new_item)
    session.commit()
