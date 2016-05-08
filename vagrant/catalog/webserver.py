from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
app = Flask(__name__)

# For login
from flask import session as login_session # Stores user
import random, string
#
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
#
CLIENT_ID = json.loads(
          open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Catalog Application"

# Import CRUD Operations
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
    # Login
    login_button = True
    if 'username' in login_session:
        login_button = False
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
    login_session['state'] = state
    print "The current session state is %s" % login_session['state']
    # Find categories
    categories = session.query(Category).all()
    # Get items made in the last week
    today = date.today()
    days_ago = 7
    recent_time = today - timedelta(days=days_ago)
    recent_items = (session.query(Item)
                           .filter(Item.date_added > recent_time)
                           .all())
    return render_template('index.html', categories=categories, STATE=state,
                           recent_items=recent_items, login_button=login_button)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print "The current session state is %s" %login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                 json.dumps("Token's user ID doesn't match given ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                 json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                 json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # TODO (VictorLoren): Create a template
    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           %login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
    	response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# Category page
@app.route('/catalog/<string:category_name>/')
def category(category_name):
    # Login
    login_button = True
    if 'username' in login_session:
        login_button = False
    # Find categories
    categories = session.query(Category).all()
    #Get items from category
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    items = session.query(Item).filter_by(category_id=cat_id)
    return render_template('category.html', categories=categories, items=items,
                           category=category_name, login_button=login_button)

# Item page
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def item(category_name, item_name):
    # Login
    login_button = True
    if 'username' in login_session:
        login_button = False
    # Find categories
    categories = session.query(Category).all()
    #Get items from category
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    item=session.query(Item).filter_by(category_id=cat_id, name=item_name).one()
    return render_template('item.html', categories=categories, item=item,
                           category=category_name, login_button=login_button)

# Add new item (new or existing category)
@app.route('/catalog/new/', methods=['GET','POST'])
def new_item():
    # Stop user from accessing if not logged in and redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    # Find categories
    categories = session.query(Category).all()
    # If user submits form to create new item
    if request.method == 'POST':
        # Check that user doesn't enter an empty string
        if request.form['newItemName'] == '':
            # Give an error message
            flash("The item wasn't added! You need to type a name!")
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
    # Stop user from accessing if not logged in and redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    # Find categories
    categories = session.query(Category).all()
    # Get category id for edited item
    oldCategory = session.query(Category).filter_by(name=category_name).first()
    old_cat_id = oldCategory.id
    item = (session.query(Item)
                   .filter_by(category_id=old_cat_id, name=item_name)
                   .one())
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
        # Get category id for new item
        cat_id = session.query(Category).filter_by(name=categoryName).first().id
        # Delete old category if this was the last item in the old category
        items_in_category = (session.query(Item)
                                    .filter_by(category_id=old_cat_id))
        num_of_items = items_in_category.count()
        # Delete old category if new category is chosen and no items left
        if num_of_items == 1 and old_cat_id != cat_id:
            session.delete(oldCategory)
        # Save edits to item
        item.name = request.form['itemName']
        item.description = request.form['itemDesc']
        item.image = request.form['itemURL']
        item.category_id = cat_id
        # Save edits officially to database
        session.add(item)
        session.commit()
        # Send a success message
        flash("Your item has been edited!")
        # Go back to main page
        return redirect(url_for('item', item_name=request.form['itemName'],
                                category_name=categoryName))
    else:
        return render_template('item-edit.html', categories=categories,
                               item=item, category=category_name)
# Delete item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET','POST'])
def delete_item(category_name, item_name):
    # Stop user from accessing if not logged in and redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
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
        # Send a success message
        flash("%s item has been deleted." %item.name)
        # Return to category page
        return redirect(url_for('catalog'))
    else:
        return render_template('item-delete.html', categories=categories,
                               item=item, category=category_name)

# Returning JSON for a category's items
@app.route('/catalog/<string:category_name>/<string:item_name>.json')
def item_json(category_name, item_name):
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    item = (session.query(Item)
                   .filter_by(category_id=cat_id, name=item_name).one())
    return jsonify(item.serialize)


# Returning JSON for a category
@app.route('/catalog/<string:category_name>.json')
def category_json(category_name):
    cat_id = session.query(Category).filter_by(name=category_name).first().id
    items = session.query(Item).filter_by(category_id=cat_id).all()
    return jsonify(Items=[i.serialize for i in items])

# Returning JSON for catalog
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
    app.secret_key = 'very_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
