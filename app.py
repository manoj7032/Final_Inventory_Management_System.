from flask import Flask, redirect, request, jsonify, render_template, url_for, session, abort
import pymysql.cursors
import bcrypt
import redis
from decimal import Decimal
import json
import sys


# Connect to Redis instance
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)



app = Flask(__name__)
app.secret_key = 'srinivasarao'  # Change this to a strong secret key in production

def db_connection():
    return pymysql.connect(host='localhost',
                           user='root',  
                           password='manoj123',  
                           db='inventory_management',
                           cursorclass=pymysql.cursors.DictCursor)


# Helper function to get user by username
def get_user_by_username(username):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
            conn.commit()
        except pymysql.err.IntegrityError:
            return "Username already exists!"
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            return "Invalid username or password!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        abort(401)  # Unauthorized access
    return render_template('dashboard.html')  # Dashboard to choose "Add New Item" or "View Items"


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/items', methods=['POST'])
def create_item():
    conn = db_connection()
    cursor = conn.cursor()
    name = request.form['name']
    quantity = request.form['quantity']
    price = request.form['price']
    sql = "INSERT INTO items (name, quantity, price) VALUES (%s, %s, %s)"
    cursor.execute(sql, (name, quantity, price))
    conn.commit()
    return jsonify({'status': 'Item added successfully'}), 201
@app.route('/items', methods=['GET'])
def read_items():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return jsonify(items), 200
@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    conn = db_connection()
    cursor = conn.cursor()
    item = request.get_json()
    name = item['name']
    quantity = item['quantity']
    price = item['price']
    sql = """
    UPDATE items
    SET name=%s, quantity=%s, price=%s
    WHERE id=%s
    """
    cursor.execute(sql, (name, quantity, price, id))
    conn.commit()
    return jsonify({'status': 'Item updated successfully'}), 200
@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    conn = db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM items WHERE id=%s"
    cursor.execute(sql, (id,))
    conn.commit()
    return jsonify({'status': 'Item deleted successfully'}), 200
@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':

        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        
       
        conn = db_connection()
        cursor = conn.cursor()
        
       
        sql = "INSERT INTO items (name, quantity, price) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, quantity, price))
        conn.commit()  
        
        
        return redirect(url_for('view_items.html'))
    else:
        
        return render_template('add_item.html')

from decimal import Decimal
import json

def default_converter(o):
    if isinstance(o, Decimal):
        return float(o)  # or str(o) if you prefer to handle it as string
    raise TypeError("Object of type 'Decimal' is not JSON serializable")

@app.route('/view-items')
def view_items():
    if cache.exists('items'):
        items = cache.get('items')
        print("Data is retrieved from cache.")
        items = json.loads(items)
    else:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        # Convert Decimal types before serialization
        for item in items:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)  # Convert Decimal to float
        cache.set('items', json.dumps(items, default=default_converter), ex=60)
        print("Data is retrieved from database.")
    return render_template('view_items.html', items=items)



    #return render_template('view_items.html', items=json.loads(items))

@app.route('/edit-item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    conn = db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
       
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        
        
        sql = "UPDATE items SET name=%s, quantity=%s, price=%s WHERE id=%s"
        cursor.execute(sql, (name, quantity, price, id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_items'))
    else:
        
        cursor.execute("SELECT * FROM items WHERE id = %s", (id,))
        item = cursor.fetchone()
        conn.close()
        if item:
            return render_template('edit_item.html', item=item)
        else:
            return 'Item not found', 404


@app.route('/delete-item/<int:id>', methods=['POST'])
def delete_items(id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_items'))


if __name__ == '__main__':
    port = 5000  # default port
    if len(sys.argv) > 1:
        port = int(sys.argv[1])  # allows specifying the port as a command line argument
    app.run(host='0.0.0.0', port=port, debug=True)

