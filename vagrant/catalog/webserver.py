from datetime import date
from flask import Flask, render_template, request, redirect, url_for, jsonify
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
        # Check that user doesn't enter an empty string
        if request.form['newItemName'] == '':
            # TODO(VictorLoren): Give an error message
            # Return to new item page
            return render_template('item-new.html', categories=categories)
        # Check if user selected "New Category" in dropdown
        if request.form['categoryName'] == 'newCategory':
            # Create new category in database from user input
            categoryName = request.form['newCat']
            newCategory = Category(name=categoryName)
            session.add(newCategory)
            session.commit()
        else:
            categoryName = request.form['categoryName']
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
        return redirect(url_for('item', item_name=request.form['newItemName'],
                                category_name=categoryName))
    # Present new item form
    else:
        return render_template('item-new.html', categories=categories)
# Edit existing item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET','POST'])
def edit_item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    # Get category id for edited item
    oldCategory = session.query(Category).filter_by(name=category_name).first()
    cat_id = oldCategory.id
    item=session.query(Item).filter_by(category_id=cat_id, name=item_name).one()
    # Edit data
    if request.method == 'POST':
        # Check if user selected "New Category" in dropdown
        if request.form['categoryName'] == 'newCategory':
            # Create new category in database from user input
            categoryName = request.form['newCat']
            newCategory = Category(name=categoryName)
            session.add(newCategory)
            session.commit()
        else:
            categoryName = request.form['categoryName']
        # Delete old category if this was the last item in the old category
        items_in_category = session.query(Item).filter_by(category_id=cat_id)
        num_of_items = items_in_category.count()
        # Delete old category
        if num_of_items == 1:
            session.delete(oldCategory)
        # Get category id for new item
        cat_id = session.query(Category).filter_by(name=categoryName).first().id
        # Save edits to item
        item.name = request.form['itemName']
        item.description = request.form['itemDesc']
        item.image = request.form['itemURL']
        item.category_id = cat_id
        # Save edits officially to database
        session.add(item)
        session.commit()
        # TODO(VictorLoren): Send a success message
        # Go back to main page
        return redirect(url_for('item', item_name=request.form['itemName'],
                                category_name=categoryName))
    else:
        return render_template('item-edit.html', categories=categories, item=item,
                            category=category_name)
# Delete item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET','POST'])
def delete_item(category_name, item_name):
    # Find categories
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).first()
    cat_id = category.id
    item=session.query(Item).filter_by(category_id=cat_id, name=item_name).one()
    if request.method == 'POST':
        # Check if this item is all that is left in category
        items_in_category = session.query(Item).filter_by(category_id=cat_id)
        num_of_items = items_in_category.count()
        # Delete item
        session.delete(item)
        # If yes, delete category after item delete
        if num_of_items == 1:
            session.delete(category)
        session.commit()
        # TODO(VictorLoren): Send a success message
        # Return to category page
        return redirect(url_for('catalog'))
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
