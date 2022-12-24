from flask import Flask, render_template, request,redirect,url_for
import db_queries as dbq
import hashlib

app=Flask(__name__)
account={}

# PAGES

@app.route('/')
def index():
    print(account)
    if not account:
        return render_template("signup.html")
    else:
        return redirect(url_for('shop'))

@app.route('/shop', methods=["GET"])
def shop():
    if account:
        categorySearched = request.args.get('itemCategory')
        products = dbq.getAllProducts()
        categories = dbq.getAllCategories()
        if categorySearched:
            products = dbq.getProductsByCategory(categorySearched)
            categorySearched = int(categorySearched)
        return render_template("shop.html",  categorySearched=categorySearched,productsList = products, account=account, categories=categories)
    else:
        return redirect(url_for('signup'))

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/profile')
def profile():
    if account:
        locations = dbq.getLocationsForUser(account['id'])
        orders = dbq.getOrders(account['id'])
        activeOrders = []
        historyOrders = []
        for order in orders:
            if order['status'] == 'Waiting':
                activeOrders.append(order)
            else:
                historyOrders.append(order)
        return render_template("profile.html", account=account, locationsList = locations, activeOrdersList = activeOrders, historyOrdersList = historyOrders)
    else:
        return redirect(url_for('signup'))

@app.route('/dashboard')
def dashboard():
    if account:
        orders = dbq.getAllOrders()
        activeOrders = []
        historyOrders = []
        for order in orders:
            if order['status'] == 'Waiting':
                activeOrders.append(order)
            else:
                historyOrders.append(order)
        categories = dbq.getAllCategories()
        return render_template("dashboard.html", categories=categories, account=account, historyOrdersList = historyOrders, activeOrdersList= activeOrders)
    else:
        return redirect(url_for('signup'))

@app.route('/cart')
def cart():
    if account:
        locations = dbq.getLocationsForUser(account['id'])
        productsInCart = dbq.getProductsInCart(account['id'])
        return render_template("cart.html", account=account,productsList = productsInCart, locationsList = locations)
    else:
        return redirect(url_for('signup'))
@app.route('/emptyCart')
def emptyCart():
    if account:
        dbq.emptyCart(account['id'])
        return redirect(url_for('shop'))
    else:
        return redirect(url_for('signup'))

@app.route('/completeOrder', methods=["POST"])
def completeOrder():
    if account:
        dbq.completeOrder(account['id'],request.form["location"])
        return render_template('thankyou.html',account=account)
    else:
        return redirect(url_for('signup'))

# DELIVERY LOCATIONS
@app.route('/addDeliveryLocation')
def locationAdd():
    if account:
        return render_template("addDeliveryLocation.html", account=account)
    else:
        return redirect(url_for('signup'))

@app.route('/create-location', methods=["POST"])
def locationCreate():
    if account:
        name = request.form['name']
        city = request.form['city']
        street = request.form['street']
        streetnr = request.form['streetnr']
        flat = request.form['flat']
        app = request.form['app']
        floor = request.form['floor']
        if name == '':
            name = "No name"
        if city == '':
            city = "No City"
        if street == '':
            street = "No Street"
        if streetnr == '':
            streetnr = 0
        if flat == '':
            flat = '-'
        if app == '':
            app = 0
        if floor == '':
            floor = 0
        
        dbq.addLocation(account['id'],city,street,streetnr,flat,app,floor,name)
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('signup'))

@app.route('/location/delete/<id>')
def deleteLocation(id):
    if account:
        dbq.deleteLocation(id)
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('signup'))
 # PRODUCT OPERATIONS

@app.route('/product/<id>')
def viewDetails(id):
    if account:
        product = dbq.getProduct(id)
        return render_template("productDetails.html", product=product, account=account)
    else:
        return redirect(url_for('signup'))

@app.route('/product/remove/<id>')
def removeProduct(id):
    if account:
        dbq.removeProduct(id)
        return redirect(url_for('shop'))
    else:
        return redirect(url_for('signup'))

@app.route('/product/edit/<id>')
def editProduct(id):
    if account:
        product = dbq.getProduct(id)
        categories = dbq.getAllCategories()
        return render_template("editItem.html", account=account,product=product, categories=categories)
    else:
        return redirect(url_for('signup'))

@app.route('/product/<id>/addToCart')
def addToCart(id):
    if account:
        dbq.addToCart(account['id'], id)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('signup'))

#LOGIN / SIGNUP 

@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.form["uname"]
    name = request.form["name"]
    passwd = request.form["password"]
    confirmPasswd = request.form["confirmPassword"]
    errors = 0
    usernameErr = ''
    passwordErr = ''
    nameError = ''
    passwordErr = ''
    confirmPassErr = ''
    if username == '':
        errors = errors + 1
        usernameErr = "You need to enter an username"
    elif dbq.userExists(username) == True:
        errors = errors + 1
        usernameErr = "Username is already taken"
    if name == '':
        errors = errors + 1
        nameError = "You need to enter a name"
    if passwd == '':
        errors = errors + 1
        passwordErr = "You need to enter a password"
    if confirmPasswd == '':
        errors = errors
        confirmPassErr = "You need to re-enter your password"
    if passwd != '' and confirmPasswd != '' and passwd != confirmPasswd:
        errors = errors + 1
        confirmPassErr = "Passwords don't match"
    if errors > 0:
        return render_template("signup.html", regconfirmpasswordError=confirmPassErr, regNameError=nameError, regpasswordError = passwordErr, regusernameError = usernameErr)
    dbq.createUser(name,passwd, username)
    global account
    account = dbq.getAccountDetails(username)
    print(account)
    return redirect(url_for('index'))

@app.route("/login", methods=["POST"])
def login():
    username = request.form["uname"]
    password = request.form["password"]
    global account 
    errors = 0
    usernameErr = ''
    passwordErr = ''
    if username == '':
        errors = errors + 1
        usernameErr = "You need to enter an username"
    elif dbq.userExists(username) == False:
        errors = errors + 1
        usernameErr = "Username doesn't exist"
    if password == '':
        errors = errors + 1
        passwordErr = "You need to enter a password"
    elif username != '' and dbq.validatePassword(username, password) == False:
        errors = errors + 1
        passwordErr = "Incorrect password"
    if errors > 0:
        return render_template("signup.html", passwordError = passwordErr, usernameError = usernameErr)
    account = dbq.getAccountDetails(username)
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    global account
    account = {}
    return redirect(url_for('index'))


# ADMIN COMMANDS
@app.route('/create-item', methods=['GET', 'POST'])
def createItem():
    name = request.form["itemName"]
    desc = request.form["itemDescription"]
    price = request.form["itemPrice"]
    image = request.files["itemImage"]
    if name == '':
        name = "No name"
    if desc == '':
        desc = "No Description"
    if price == '':
        price=0
    imageSrc = 'static/'
    if image.filename != '':
        extension = image.filename.split(".")[-1]
        image.save("/var/www/python/flask-ecommerce/static/" + name + '.' + extension)
        imageSrc = 'static/' + name+'.'+extension
    category = request.form["itemCategory"]
    stock = request.form["itemStock"]
    if stock == '':
        stock = 0
    if category == '':
        category = 0
    dbq.addItem(name,desc,price,imageSrc,category,stock)
    return redirect(url_for('index'))

@app.route('/edit-item/<id>', methods=['POST'])
def editItem(id):
    name = request.form["itemName"]
    desc = request.form["itemDescription"]
    price = request.form["itemPrice"]
    image = request.files["itemImage"]
    if name == '':
        name = "No name"
    if desc == '':
        desc = "No Description"
    if price == '':
        price='0'
    imageSrc = ''
    if image.filename != '':
        extension = image.filename.split(".")[-1]
        image.save("/var/www/python/flask-ecommerce/static/" + name + '.' + extension)
        imageSrc = 'static/' + name+'.'+extension
    category = request.form["itemCategory"]
    stock = request.form["itemStock"]
    dbq.editItem(id,name,desc,price,imageSrc,category,stock)
    return redirect(url_for('index'))

@app.route("/create-category", methods=["GET","POST"])
def createCategory():
    name = request.form["categoryName"]
    dbq.addCategory(name)
    return redirect(url_for('index'))

@app.route('/add-item')
def addItem():
    if account:
        categoriesList = dbq.getAllCategories()
        return render_template("addItem.html", categories = categoriesList, account=account)
    else:
        return redirect(url_for('signup'))

@app.route('/add-category')
def addCategory():
    if account:
        return render_template("addCategory.html", account=account)  
    else:
        return redirect(url_for('signup')) 
@app.route('/delete-category/<id>', methods=["GET"])
def removeCategory(id):
    if account:
        dbq.deleteCategory(id)
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('signup'))
@app.route('/markAsDelivered/<orderId>', methods=["POST"])
def markAsDelivered(orderId):
    if account:
        dbq.markAsDelivered(orderId)
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))