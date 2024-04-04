from flask import Flask, render_template, request, redirect,session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import redirect

app = Flask(__name__,  template_folder='C:/Users/anish/Desktop/Frontend_Lab/DBMS_frontend/src')

# Configure MySQL
app.secret_key = 'abcd2123445'  
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@B203kairavi'
app.config['MYSQL_DB'] = 'lab_bookings'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Fetch form data
        details = request.form
        name = details['name']
        lab_name = details['lab_name']
        date_from = details['date_from']
        date_to = details['date_to']
        time = details['time']

        # Insert into MySQL
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO bookings (name, lab_name, date_from, date_to, time) VALUES (%s, %s, %s, %s, %s)", (name, lab_name, date_from, date_to, time))
        mysql.connection.commit()
        cur.close()

        return render_template('submit.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch user from database
        # cur = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['email'] = user['email']
            return redirect(url_for('booking_lab'))
        # cursor.close()

        # if user:
        #     # Redirect to booking page if login is successful
        #     return render_template('/bookinglab.html')
        else:
            # Redirect to login page with error message if login fails
            return render_template('login.html', error="Invalid email or password")
        
        
        mesage = ''
    # if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
    #     email = request.form['email']
    #     password = request.form['password']
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
    #     user = cursor.fetchone()
    #     if user:
    #         session['loggedin'] = True
    #         session['userid'] = user['id']
    #         session['name'] = user['first_name']
    #         session['email'] = user['email']
    #         session['role'] = user['role']
    #         mesage = 'Logged in successfully !'            
    #         return redirect(url_for('dashboard'))
    #     else:
    #         mesage = 'Please enter correct email / password !'
    # return render_template('login.html', mesage = mesage)
    
    if request.method == 'GET':
        return render_template('login.html')
    
    return render_template('login.html')
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['reg_email']
        password = request.form['reg_password']

        # Insert new user into database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()

        # Redirect to login page after successful registration
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('register.html')

@app.route('/bookinglab')
def booking_lab():
    if 'loggedin' in session:
        return render_template('bookinglab.html')
    return redirect(url_for('login'))

  
if __name__ == '__main__':
            
    app.run(debug=True)
