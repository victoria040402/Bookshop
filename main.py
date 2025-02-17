from flask import Flask                 #imports all the flask libraries required
from markupsafe import escape
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import abort
from flask import make_response
from flask import session
import sqlite3                         #imports sqlite3
app = Flask(__name__)
app.secret_key="secret key"
@app.route('/register', methods=['GET', 'POST'])     #register webpage with get and post methods, 
                                                     #app route defines what must go at the end of 
                                                     #the url to run the following functions.    
def register():
    if request.method == 'POST':                                                #registration form to allow the users to post in request forms username and password.
        return do_the_registration(request.form['uname'], request.form['pwd'])
    else:
        return show_the_registration_form();                                    #returns blank registration form page
def show_the_registration_form():
    return render_template('register.html',page=url_for('register'))            #returns registration page
def do_the_registration(u,p):
    con = sqlite3.connect('mydatabase.db')                                      #connects to 'mydatabase'
    try:                                              
        con.execute('CREATE TABLE users (name TEXT, pwd INT)')                  #creates table to store the username and password entered through registration.
        print ('Table created successfully');
    except:
        pass                                                                    #exception to prevent a duplicate table being created
    
    con.close()                                                                 #closes connection to 'mydatabase'
    con = sqlite3.connect('mydatabase.db')                                      #reopens connection to 'mydatabase'
    con.execute("INSERT INTO users values(?,?);", (u, p))                       #inserts the username and password enetered into my database
    con.commit()                                                                #commits current statement executed
    con.close()                                                                 #closes connection to 'mydatabase'
    return show_the_login_form()                                                #returns user to login page which shows login form
@app.route('/login', methods=['GET', 'POST'])                                   #login webpage using 'get' and 'post' methods, /login at end of url to reach this webpage to run the functions
def login():                                                                    # function defined as login
    if request.method == 'POST':                    
        return do_the_login(request.form['uname'], request.form['pwd'])         #shows login form, similar to registration form
    else:
        return show_the_login_form()                                            #returns blank login form
def show_the_login_form():
    return render_template('login.html',page=url_for('login'))                  #returns login form 


def do_the_login(u,p):                                                          #function called do the login
    con = sqlite3.connect('mydatabase.db')                                      #connects to 'mydatabase'
    cur = con.cursor();                                    
    cur.execute("SELECT count(*) FROM users WHERE name=? AND pwd=?;", (u, p))   #calls for the username and password so it can check if in table
    if(int(cur.fetchone()[0]))>0:                                               #saves u in session and loops through table to check details are correct
        session['username']= u
        return homepage()                                                       #if correct details entered, user returned to homepage
    else:
        abort(403)                                                              #if details entered are incorrect error handler is called
@app.errorhandler(403)
def wrong_details(error):
    return render_template('wrong_details.html'), 403                           #calls for webpage displaying error message.
@app.route('/add_books', methods=['GET', 'POST'])                               #app route to add books to stock, uses 'get' and 'post' methods
def add_books():                                  
    if request.method == 'POST':                                                #function add_books uses a request form to get all the necessary details of the books
        return do_the_add(request.form['ISBN13_number'], request.form['name'], request.form['author'], request.form['publication_date'], request.form['cover'], request.form['book_description'], request.form['trade_price'], request.form['retail_price'], request.form['quantity'])
    else:
        return show_add_books_form();
def show_add_books_form():                                                      #function show_add_books_form returns the form page
    return render_template('add_books.html', page=url_for('add_books'))
def do_the_add(isbn, name, author, date, image, descrip, trade, retail, quantity):      #function do_the_add uses 9 arguments
    con=sqlite3.connect('mydatabase.db')                                                #connects to 'mydatabase'
    cur = con.cursor()      
    rows=cur.execute("SELECT quantity FROM books WHERE ISBN13_number=?", (str(isbn),)).fetchall()  #selects books in table if it matches the isbn
    quantity=int(quantity)                                                              #quantity set as integer
    if len(rows) == 1:                                                                  
        current_quantity=int(rows[0][0])
        updated_quantity=current_quantity + quantity                                    #if statement to update the quantity of the books
        if int(updated_quantity) < 21:
                con.execute("UPDATE books SET quantity = ? WHERE ISBN13_number=?",(updated_quantity,isbn))  #updates number of specific book in stock
                con.commit()
        else:
                updated_quantity=20                                                     #if updated_quantity exceeds 20 the updated_quantity is capped at 20
                con.execute("UPDATE books SET quantity = ? WHERE ISBN13_number=?",(updated_quantity,isbn)) # quantity in stock updated in table
                con.commit()
    else:
        if quantity > 20:                                                               #if book not already in table, adds the new book
            quantity=20
        con.execute("INSERT INTO books values(?, ?, ?, ?, ?, ?, ?, ?, ?);", (isbn, name, author, date, image, descrip, trade, retail, quantity))  #inserts the details of the new book into table
        con.commit()
    con.close()                                           #closes connection to database
    return show_add_books_form()                          #returns the form to add books
@app.route('/homepage')                                   #app route for homepage
def homepage():                                           #function defined as homepage
    con=sqlite3.connect('mydatabase.db')                  #connects to 'mydatabase'
    try:
        con.execute('CREATE TABLE books(ISBN13_number INT, name TEXT, author TEXT, publication_date DATE, cover TEXT, book_description TEXT, trade_price INT, retail_price INT, quantity INT)')  #creates table to store books if one is not already created
        print('success');
    except:
        pass                              #else no new table created
    try:
        con.close()                       #connect to database closed
        con = sqlite3.connect('mydatabase.db')  #connection to database opens
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT ISBN13_number, name, cover, retail_price from books WHERE quantity > 0")  #selects only books that are currently in stock from table books
        rows = cur.fetchall();               #fetches all the books that meet the requirement
        return render_template('homepage.html', rows = rows)  #returns homepage
    except Exception as e:
        print(e)
    finally:
        con.close()                            #closes connection to database
        return render_template('homepage.html', rows = rows) #returns homepage
@app.route('/purchasedhomepage')
def pur_homepage():
    return render_template('purchasedhomepage.html', page=url_for('pur_homepage')) #returns webpage 'purchasedhomepage.html'
@app.route('/stock_levels')
def stock_levels():                                #function for displaying stock levels
    con=sqlite3.connect('mydatabase.db')           #connects to database
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("SELECT * FROM books")             #selects all details from books
    rows = cur.fetchall();                       
    return render_template('stock_levels.html', rows=rows) #returns webpage to display stock details
@app.route('/add_to_cart', methods=['POST','GET'])         
def add_book_to_cart():                            #function to add book to cart
    cursor=None                                    #sets cursor as none
    con=sqlite3.connect('mydatabase.db')           #connects to database
    _quantity = int(request.form['quantity'])      #quantity input set as _quantity
    _ISBN13_number = int(request.form['ISBN13_number']) #isbn number set as _ISBN13_number
    if _quantity and _ISBN13_number and request.method == 'POST': #if data posted then:
        cursor=con.cursor()
        cursor.execute("SELECT * FROM books WHERE ISBN13_number=?", (_ISBN13_number,))  #selects everything from books where isbn number posted matches
        rows=cursor.fetchone()
        itemDict={'ISBN13_number': rows[0], 'name':rows[1], 'cover':rows[4], 'quantity': _quantity, 'retail_price': rows[7], 'total_price' : _quantity * rows[7]} #dictionary with the corresponding variables
        all_total_price=0                              #all_total_price set as 0
        all_total_quantity=0                           #all_total_quantity set as 0
        session.modified=True                       #session.modified set as true
        ISBN=str(rows[0])                           #isbn made into string
        if 'cart_item' in session:                  #if the cart item is in the session
            if ISBN in session['cart_item']:        #and if the isbn is mathing to cart item in session
                for key, value in session['cart_item'].items():   #for that isbn in the session
                    if ISBN == key:                               
                        old_quantity=session['cart_item'][key]['quantity']  #quantity is increased as that book is already in cart 
                        total_quantity= old_quantity + _quantity
                        session['cart_item'][key]['quantity']= total_quantity        #session for price and quantity of specific cart item is updated
                        session['cart_item'][key]['total_price']= total_quantity * rows[7]
            else:
                session['cart_item'][ISBN]=itemDict     #else add new item to cart
        else:
            session['cart_item'] = { ISBN : itemDict }
        for key, value in session['cart_item'].items():             
            individual_quantity= session['cart_item'][key]['quantity']   #calculate individual quantity and price for cart item
            individual_price= session['cart_item'][key]['total_price']
            all_total_quantity = all_total_quantity + individual_quantity #add previous all_total_quantity to new individual_quantity
            all_total_price = all_total_price + individual_price          #add previous all_total_price to new individual_price
        session['all_total_quantity'] = str(all_total_quantity)           #session values updated
        session['all_total_price'] = str(all_total_price)
        con.close()                                                        #closes connection to database
    else:
        con.close()
        return "Error while adding item to cart"
    return homepage()                                                   #returns homepage
@app.route('/empty')
def empty_cart():
    session.clear()                                                     #clears the session
    return homepage()                                                   #returns homepage, cart will appear empty
@app.route('/delete/<string:ISBN13_number>') 
def delete_book(ISBN13_number):
    all_total_price=0
    all_total_quantity=0
    session.modified=True
    if ISBN13_number in session['cart_item']:                #if idbn in cart
        item = session['cart_item'][ISBN13_number]           #item equals the isbn in cart
        if item['quantity'] == 1:                            #if the item quantity is equal to 1 then session gets cleared
            del session['cart_item'][ISBN13_number]
        else:
            item['quantity'] = item['quantity'] - 1           #else item quantity is reduced by 1
            item['total_price'] = item['quantity'] * item['retail_price'] #new total_price for books is set
            session['cart_item'][ISBN13_number] = item
        for key, value in session['cart_item'].items():             
            individual_quantity= session['cart_item'][key]['quantity']         
            individual_price= session['cart_item'][key]['total_price']
            all_total_quantity = all_total_quantity + individual_quantity
            all_total_price = all_total_price + individual_price
        session['all_total_quantity'] = all_total_quantity          #repeated process above and session variables are updated
        session['all_total_price'] = all_total_price
    return redirect(url_for('homepage'))                       #returns homepage
@app.route('/checkout')
def checkout():                                               #function called checkout
    for key, value in session['cart_item'].items():
        db_quantity_books, book_price = get_stock_level(key)         #for each key in session get_stock_level is run for it using values returned from function
        if db_quantity_books < session['cart_item'][key]['quantity']:
            individual_quantity=db_quantity_books
            individual_price= db_quantity_books * book_price
            session['all_total_price']=int(session['all_total_price']) - int(session['cart_item'][key]['total_price'])  #this section of code checks the number in stock is less than that requested, if true then then number purchasable is reduced to the number in stock and the session totals are updated
            session['all_total_quantity']=int(session['all_total_quantity']) - int(session['cart_item'][key]['quantity'])
            session['cart_item'][key]['quantity']=individual_quantity
            session['cart_item'][key]['total_price']=individual_price
            session['all_total_price']+= individual_price
            session['all_total_quantity']+= individual_quantity
            print(f"ISBN: {key}, Quantity: {individual_quantity}, Total Price: {individual_price}")
    postage = (int(session['all_total_quantity'])-1) + 3   #calculates the postage cost
    session['all_total_price']= postage + int(session['all_total_price']) #session for all_total_price is updated to include postage cost
    return render_template('checkout.html', page=url_for('checkout')) #returns checkout page
@app.route('/pay_now', methods=['GET', 'POST'])
def pay_now():
    for key, value in session['cart_item'].items():   
        remove_stock(key, session['cart_item'][key]['quantity'])      #for each key purchased remove_stock function is run
    return render_template('pay_now.html', page=url_for('pay_now'))   #returns pay now webpage
def remove_stock(isbn13, sold_quantity):                       #remove_stock function with 2 arguments
    con=sqlite3.connect('mydatabase.db')                       #connects to database
    con.row_factory=sqlite3.Row
    cur=con.cursor()
    cur.execute("SELECT quantity FROM books WHERE ISBN13_number=?", (isbn13,)) #selects quantity for books purchased
    rows=cur.fetchone()
    current_quantity=int(rows[0])               #current_quantity set as int
    new_quantity= current_quantity - sold_quantity #new_quantity set to then update table with new values
    cur.execute("UPDATE books SET quantity = ? WHERE ISBN13_number=?", (new_quantity, isbn13)) #table is updated
    con.commit()   
    con.close()            #connection to database closes
def get_stock_level(isbn_number):    #function get_stock_level with 1 argument
    con=sqlite3.connect('mydatabase.db') #connects to database
    con.row_factory=sqlite3.Row
    cur=con.cursor() 
    cur.execute("SELECT quantity, retail_price FROM books where ISBN13_number=?", (isbn_number,)) #selects quantity and retail_price for the books in cart
    rows=cur.fetchone()
    db_quantity_books=int(rows[0]) #quantity is set as db_quantity_books
    book_price=int(rows[1]) #retail_price is set as book_price
    con.close()               #connection to database closed
    return db_quantity_books, book_price  #returns the values db_quantity_books and book_price
