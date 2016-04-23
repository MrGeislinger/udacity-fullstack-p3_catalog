from flask import Flask, render_template, jsonify
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
    with open('templates/styles.css','r') as stylesheet:
        output = stylesheet.read()
    return output

# Home page
@app.route('/')
@app.route('/catalog/')
def catalog():
    # Find categories
    categories = session.query(Category).all()
    # TODO(VictorLoren): Read in recent items (make it a list)
    recent_items = []
    return render_template('index.html', categories=categories,
                            recent_items=recent_items)

# Category page
@app.route('/catalog/<string:category_name>/')
def category(category_name):
    # Find categories
    categories = session.query(Category).all()
    #Get items from category
    cat_id = session.query(Category).filter(Category.name == category_name)\
             .first().id
    items = session.query(Item).filter(Item.category_id == cat_id)
    return render_template('category.html', categories=categories, items=items,
                            category=category_name)

# Item page
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    #Get items from category
    cat_id = session.query(Category).filter(Category.name == category_name)\
             .first().id
    item = session.query(Item).filter(Item.category_id == cat_id,
                                      Item.name == item_name).one()
    return render_template('item.html', categories=categories, item=item,
                            category=category_name)

# Returning JSON for a category's items
@app.route('/catalog/<string:category_name>.json')
def category_json(category_name):
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    items = session.query(Item).filter_by(category_id=cat_id).all()
    return jsonify(Items=[i.serialize for i in items])

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
