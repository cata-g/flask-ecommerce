import mysql.connector
import shortuuid

database = mysql.connector.connect(
    host="localhost",
    user="flask_user",
    password="1234",
    database="flask_ecommerce"
)

cursor = database.cursor()

def getAllProducts():
    cursor.execute("SELECT * FROM products;")
    productsArray = cursor.fetchall()
    productsList = []
    for i in productsArray:
        productsList.append(
            {
                'id': i[0],
                'name': i[1],
                'price': i[2],
                'description': i[3],
                'imageSrc': i[4]
            }
        )
    return productsList

def getProduct(id):
    cursor.execute("SELECT * FROM products WHERE id={id};".format(id=id))
    productDetails = cursor.fetchone()
    product = {
        'id': productDetails[0],
        'name': productDetails[1],
        'price': productDetails[2],
        'description': productDetails[3],
        'imageSrc': productDetails[4],
        'stock': productDetails[5],
    }
    cursor.execute("SELECT name FROM categories WHERE id={id}".format(id=productDetails[6]))
    category = cursor.fetchone()
    if  type(category) is None:
        product['category'] = "Unassigned"
    else:
        product['category'] = category[0]
    return product

def getProductsByCategory(catId):
    cursor.execute("SELECT * FROM products WHERE categoryID={};".format(catId))
    productsArray = cursor.fetchall()
    productsList = []
    for i in productsArray:
        productsList.append(
            {
                'id': i[0],
                'name': i[1],
                'price': i[2],
                'description': i[3],
                'imageSrc': i[4]
            }
        )
    return productsList

def removeProduct(id):
    cursor.execute("DELETE FROM products WHERE id = {};".format(id))
    database.commit()

def getAllCategories():
    cursor.execute("SELECT * FROM categories;")
    categoriesArray = cursor.fetchall()
    categoriesList = []
    for i in categoriesArray:
        categoriesList.append(
            {
                'id': i[0],
                'name': i[1],
            }
        )
    return categoriesList

def getAccountDetails(username):
    cursor.execute("SELECT * FROM users WHERE username = '{}'".format(username))
    accountDetails = cursor.fetchone()
    account = {
        'id': accountDetails[0],
        'username': username,
        'name': accountDetails[2],
        'password': accountDetails[3],
        'role': accountDetails[4]
    }
    return account

def getUsername(userId):
    selectString = "Select username from users where id={}".format(userId)   
    cursor.execute(selectString)
    username = cursor.fetchone()
    return username[0]


def createUser(name, password, username):
    createString = "INSERT INTO users(username,name,password) VALUES ({username}, {name}, {password});".format(username='"'+username+'"', name='"'+name+'"', password='"'+password+'"')
    cursor.execute(createString)
    database.commit()

def userExists(username):
    searchString = "SELECT * from users WHERE username = '{}';".format(username)
    cursor.execute(searchString)
    user = cursor.fetchone()
    if user:
        return True
    return False

def validatePassword(username, password):
    searchString = "SELECT password from users where username='{}'".format(username)
    cursor.execute(searchString)
    passwordInDB = cursor.fetchone()[0]
    if password == passwordInDB:
        return True
    return False

def addItem(name,desc, price, imageSrc, category, stock):
    createString = "INSERT INTO products(name, price, description, imageSrc, stock, categoryID) VALUES ({name}, {price}, {description}, {imageSrc}, {stock}, {category});".format(name='"'+name+'"', price=price, description='"'+desc+'"', imageSrc='"'+imageSrc+'"', stock=stock, category=category)
    cursor.execute(createString)
    database.commit()

def editItem(id,name,desc, price, imageSrc, category, stock):
    updateString= "UPDATE products SET "
    updateString += "name={}, ".format('"'+name+'"')
    updateString += "price={}, ".format('"'+price+'"')
    updateString += "description={}, ".format('"'+desc+'"')
    if imageSrc != '':
        updateString += "imageSrc={}, ".format('"'+imageSrc+'"')
    updateString += "stock={}, ".format(stock)
    updateString += "categoryID={} ".format(category)
    updateString += "WHERE id={};".format(id)
    cursor.execute(updateString)
    database.commit()

def addCategory(name):
    createStringCategory = "INSERT INTO categories (name) VALUES ('{}');".format(name)
    cursor.execute(createStringCategory)
    database.commit()
def deleteCategory(categoryId):
    updateString = "UPDATE products SET categoryID=0 WHERE categoryID={};".format(categoryId)
    cursor.execute(updateString)
    database.commit()
    deleteStringCategory = "DELETE FROM categories WHERE id={}".format(categoryId)
    cursor.execute(deleteStringCategory)
    database.commit()

def addToCart(user_id, product_id):
    addToCartString = "INSERT INTO cart (user_id, product_id) VALUES ('{user}', '{product}');".format(user=user_id, product=product_id)
    cursor.execute(addToCartString)
    database.commit()
def getProductsInCart(user_id):
    getProductsIds = "SELECT product_id FROM cart WHERE user_id={};".format(user_id)
    cursor.execute(getProductsIds)
    productIDS = cursor.fetchall()
    productsInfo = []
    print(productIDS)
    for id in productIDS:
        productsInfo.append(getProduct(id[0]))
    return productsInfo
def emptyCart(userId):
    removeProducts = "DELETE FROM cart WHERE user_id={}".format(userId)
    cursor.execute(removeProducts)
    database.commit()
def completeOrder(user_id,loc_id):
    id = shortuuid.uuid()
    status = "Waiting"
    products = getProductsInCart(user_id)
    for product in products:
        string = "INSERT INTO orders (id, product_id, user_id, status, location_id) VALUES ('{}', {}, {}, '{}', {});".format(id, product['id'], user_id, status, loc_id)
        cursor.execute(string)
        database.commit()
        substractStock(product['id'])
    emptyCart(user_id)
def getOrders(user_id):
    getOrdersString = "SELECT * FROM orders where user_id={};".format(user_id)
    cursor.execute(getOrdersString)
    ordersFetch = cursor.fetchall()
    orders = []
    for order in ordersFetch:
        id = order[0]
        status = order[3]
        location = getLocation(order[4])
        product = getProduct(order[1])
        user = getAccountDetails(getUsername(order[2]))
        orders.append(
            {
                'id': id,
                'status': status,
                'location': location,
                'product': product,
                'user': user
            }
        )
    return orders
def getAllOrders():
    getOrdersString = "SELECT * FROM orders;"
    cursor.execute(getOrdersString)
    ordersFetch = cursor.fetchall()
    orders = []
    for order in ordersFetch:
        id = order[0]
        status = order[3]
        location = getLocation(order[4])
        product = getProduct(order[1])
        user = getAccountDetails(getUsername(order[2]))
        orders.append(
            {
                'id': id,
                'status': status,
                'location': location,
                'product': product,
                'user': user
            }
        )
    return orders
def markAsDelivered(orderId):
    updateString = "UPDATE orders SET status='Delivered' where id='{}';".format(orderId)
    cursor.execute(updateString)
    database.commit()
def substractStock(productId):
    selectString = cursor.execute("SELECT stock FROM products WHERE id={};".format(productId))
    stock = cursor.fetchone()[0]
    newStock = stock - 1
    updateString = "UPDATE products SET stock={newStock} WHERE id={id}".format(newStock = newStock, id = productId)
    cursor.execute(updateString)
    database.commit()
def addLocation(user_id, city, street, streetNr, flat, app, floor, name):
    addLocationString = "INSERT INTO locations (user_id, city, street, streetNr, flat, app, floor, name) VALUES({}, '{}', '{}',{},'{}','{}','{}', '{}');".format(user_id,city,street,streetNr,flat,app,floor,name)
    cursor.execute(addLocationString)
    database.commit()
def deleteLocation(id):
    deleteLocationString = "DELETE FROM locations WHERE id={};".format(id)
    cursor.execute(deleteLocationString)
    database.commit()
def getLocation(id):
    selectString = "SELECT * FROM locations WHERE id={};".format(id)
    cursor.execute(selectString)
    location = cursor.fetchone()
    locationDetail = {
                'id': location[0],
                'user_id': location[1],
                'city': location[2],
                'street': location[3],
                'streetNr': location[4],
                'flat': location[5],
                'apartament': location[6],
                'floor':location[7],
                'name': location[8]
            }
    return locationDetail
def getLocationsForUser(user_id):
    selectString = "SELECT * FROM locations WHERE user_id={};".format(user_id)
    cursor.execute(selectString)
    locations = cursor.fetchall()
    locationsDetails = []
    for i in locations:
        locationsDetails.append(
            {
                'id': i[0],
                'user_id': i[1],
                'city': i[2],
                'street': i[3],
                'streetNr': i[4],
                'flat': i[5],
                'apartament': i[6],
                'floor':i[7],
                'name': i[8]
            }
        )
    return locationsDetails

# VALIDARE EMAIL DACA EXISTA
# VALIDARE USERNAME DACA EXISTA
# VALIDARE PAROLE INTRE ELE
# VALIDARE CAMPURI GOALE