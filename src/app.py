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
    # if request.method == 'POST':
    #     details = request.form
    #     email = session.get('email')
    #     # Fetch form data
    #     details = request.form
    #     name = details['name']
    #     lab_name = details['lab_name']
    #     date_from = details['date_from']
    #     date_to = details['date_to']
    #     time = details['time']

    #     # Insert into MySQL
    #     cur = mysql.connection.cursor()
    #     cur.execute("INSERT INTO bookings (name, lab_name, date_from, date_to, time) VALUES (%s, %s, %s, %s, %s)", (name, lab_name, date_from, date_to, time))
    #     mysql.connection.commit()
    #     cur.close()
        
    if request.method == 'POST':
        details = request.form
        email = session.get('email')  # Retrieve email from session

        # Check if the form is for lab booking or equipment issuing
        if 'lab_name' in details:
                # Lab booking form data
                name = details['name']
                lab_name = details['lab_name']
                time_from = details['time_from']
                time_to= details['time_to']
                date= details['date']
                
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO bookings (user_email,name,lab_name,time_from, time_to,date) VALUES (%s,%s, %s, %s, %s, %s)", (email,name, lab_name, time_from, time_to,date))
                mysql.connection.commit()
                cur.close()
                          
        else:
                # Equipment issuing form data
                equipment_type = details['equipmentType']
                number_of_equipment = details['numberOfEquipment']
                issue_date = details['issueDate']
                return_date = details['returnDate']

                # Insert equipment issuing data into EquipmentIssued table
                # sql = "INSERT INTO EquipmentIssued (user_email, equipment_type, number_of_equipment, issue_date, return_date) VALUES (%s, %s, %s, %s, %s)"
                # val = (email, equipment_type, number_of_equipment, issue_date, return_date)
                
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO EquipmentIssued (user_email, equipment_type, number_of_equipment, issue_date, return_date) VALUES (%s, %s, %s, %s, %s)", (email, equipment_type, number_of_equipment, issue_date, return_date))
                mysql.connection.commit()
                cur.close()
                
        # lab_bookings = fetch_lab_bookings(email)
        lab_bookings=fetch_lab_bookings(email)
        equipment_issued = fetch_equipment_issued(email)
        return render_template('submit.html', equipment_issued=equipment_issued, lab_bookings=lab_bookings)
        # return render_template('submit.html')

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

def fetch_lab_bookings(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bookings WHERE user_email = %s", (email,))
    lab_bookings = cur.fetchall()  # Fetch all rows

    return lab_bookings

def fetch_equipment_issued(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM EquipmentIssued WHERE user_email = %s", (email,))
    equipment_issued = cur.fetchall()  # Fetch all rows
    
    return equipment_issued

# @app.route('/submit')
# def new_submit():
#     # Fetch lab bookings and equipment issued for the current user
    
#     email=session.get('email')  # Assuming you have a function to get the current user's ID
#     lab_bookings = fetch_lab_bookings(email)
#     equipment_issued = fetch_equipment_issued(email)
    
#     return render_template('submit.html', lab_bookings=lab_bookings, equipment_issued=equipment_issued)



if __name__ == '__main__':
            
    app.run(debug=True)
