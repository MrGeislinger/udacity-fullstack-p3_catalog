from datetime import date
from flask import Flask, render_template, request, redirect, url_for
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
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    items = session.query(Item).filter_by(category_id=cat_id)
    return render_template('category.html', categories=categories, items=items,
                            category=category_name)

# Item page
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    #Get items from category
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    item=session.query(Item).filter_by(category_id=cat_id, name=item_name).one()
    return render_template('item.html', categories=categories, item=item,
                            category=category_name)

# Add new item (new or existing category)
@app.route('/catalog/new/', methods=['GET','POST'])
def new_item():
    # Find categories
    categories = session.query(Category).all()
    # If user submits form to create new item
    if request.method == 'POST':
        # Check if category already exists, then use that category id
        categoryName = request.form['categoryName']
        category = session.query(Category).filter_by(name=categoryName).first()
        # If not, create new category in database
        if category == None:
            newCategory = Category(name=categoryName)
            session.add(newCategory)
            session.commit()
        # Get category id for new item
        cat_id = session.query(Category).filter_by(name=categoryName).first().id
        newItem = Item(name=request.form['newItemName'],
                       description=request.form['newItemDesc'],
                       date_added=date.today(),
                       image=request.form['newItemURL'],
                       category_id=cat_id)
        session.add(newItem)
        session.commit()
        # Send a success message
        # Go back to main page
        return redirect(url_for('catalog'))
    # Present new item form
    else:
        return render_template('item-new.html', categories=categories)
# Edit existing item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def edit_item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    # Check if category is changed
    # If new category, create new category
    # Edit data
    # Send a success message
    return render_template('item-edit.html', categories=categories, item=item,
                            category=category_name)
# Delete item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET','POST'])
def delete_item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    item=session.query(Item).filter_by(category_id=cat_id, name=item_name).one()
    if request.method == 'POST':
        # Check if this item is all that is left in category
        # If yes, delete category after item delete
        # Delete item
        session.delete(item)
        session.commit()
        # Send a success message
        # Return to category page
        return redirect(url_for('category', category_name=category_name))
    else:
        return render_template('item-delete.html', categories=categories,
                                item=item, category=category_name)

# Returning JSON for a category's items
@app.route('/catalog/<string:category_name>.json')
def category_json(category_name):
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    items = session.query(Item).filter_by(category_id=cat_id).all()
    return jsonify(Items=[i.serialize for i in items])

# Returning JSON for a category's items
@app.route('/catalog.json')
def catalog_json():
    categories = session.query(Category).all()
    serializedCategories = []
    for c in categories:
        # Find all this category's items
        items = session.query(Item).filter_by(category_id = c.id).all()
        serializedItems = []
        for i in items:
            serializedItems.append(i.serialize)
        # Add data into this category
        category = c.serialize
        category['Items'] = serializedItems
        serializedCategories.append(category)
    return jsonify(Category=serializedCategories)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
