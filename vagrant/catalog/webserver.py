from flask import Flask
app = Flask(__name__)

# Import CRUD Operations from Lesson 1
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog import Base, Category, Item

# Create session and connect to DB
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# CSS
@app.route('/styles.css')
def style():
    with open('website_template/styles.css','r') as stylesheet:
        output = stylesheet.read()
    return output

# Home page
@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    # Find categories
    output_categories = []
    for category in categories:
        category_path = category.name
        output_categories.append('<a href="catalog/%s"><h3>%s</h3></a>'
                                 % (category_path, category.name) )
    all_categories = ''.join(output_categories)
    # Find recent items
    output_recent_items = []
    all_recent_items = ''.join(output_recent_items)
    # TODO(VictorLoren): Read in recent items (make it a list)
    # Read in HTML template and replace parts
    with open('website_template/index.html','r') as html_file:
        output = html_file.read()\
                 .replace('%CATEGORIES', all_categories)\
                 .replace('%RECENT_ITEMS', all_recent_items)
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
