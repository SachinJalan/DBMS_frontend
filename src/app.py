from flask import Flask, render_template, request, redirect,session, url_for
# from Flask-MySQLdb import MySQL
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import redirect
import os

# app = Flask(__name__,  template_folder='C:/Users/anish/Desktop/Frontend_Lab/DBMS_frontend/src')

# Get the absolute path of the directory where this file is located
dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder=dir_path)

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
        
        elif 'Equipment_Name' in details:
                # Equipment issuing form data
                equipment_name = details['Equipment_Name']
                equipment_id= details['ID']
                quantity = details['Quantity']
                price= details['Price']
                vendor_address= details['Vendor_Address']
                vendor_phone_number= details['Vendor_Phone_Number']
                manufacturer_name= details['Manufacturer_Name']
                status= details['Status']
                lab_name= details['Lab_Name']
                
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO inventory ( ID,Equipment_Name, Quantity, Price, Vendor_Address, Vendor_Phone_Number, Manufacturer_Name,  Status ,  Lab_Name )  VALUES (%s, %s,%s, %s, %s, %s, %s, %s,%s)", (equipment_id,equipment_name, quantity, price, vendor_address, vendor_phone_number, manufacturer_name, status, lab_name))
                mysql.connection.commit()
                cur.close()
        
        elif 'Enrolled_Course_ID' in details:
                enrolled_course_id= details['Enrolled_Course_ID'][1:-1]                
                enrolled_course_id=enrolled_course_id.split(',')
                for i in range(len(enrolled_course_id)):
                    enrolled_course_id[i]=enrolled_course_id[i][1:-1].strip()
            
                cur = mysql.connection.cursor()
                enrolled_course_id=enrolled_course_id[0]
                cur.execute("INSERT INTO student_enrolled (Course_Id, email) VALUES (%s, %s)", (enrolled_course_id,email))
                mysql.connection.commit()
                cur.close()
          
        elif 'Course_Name' in details:
            # print("Hello")
            course_name= details['Course_Name']
            course_id= details['Course_ID']
            credits= details['Credits']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO course (email,Course_ID, Course_Name, Credits) VALUES (%s,%s, %s, %s)", (email,course_id,course_name, credits))
            mysql.connection.commit()    
            cur.close()
                
        else:
                # Equipment issuing form data
                equipment_type = details['equipmentType']
                number_of_equipment = details['numberOfEquipment']
                issue_date = details['issueDate']
                return_date = details['returnDate']
                
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO EquipmentIssued (user_email, equipment_type, number_of_equipment, issue_date, return_date) VALUES (%s, %s, %s, %s, %s)", (email, equipment_type, number_of_equipment, issue_date, return_date))
                mysql.connection.commit()
                cur.close()
                
        lab_bookings=fetch_lab_bookings(email)
        equipment_issued = fetch_equipment_issued(email)
        courses=fetch_courses()
        return render_template('submit.html', equipment_issued=equipment_issued, lab_bookings=lab_bookings,courses=courses)

@app.route('/profile')
def profile():
    email=session.get('email')
    lab_bookings=fetch_lab_bookings(email)
    equipment_issued = fetch_equipment_issued(email)
    role=fetch_role(email)
    name=fetch_name(email)
    if(role=='student'):
        courses=fetch_student_courses(email)
        return render_template('profile.html', equipment_issued=equipment_issued, lab_bookings=lab_bookings,courses=courses,name=name,role = role)
    elif(role=='professor'):
        courses=fetch_prof_course(email)
        return render_template('profile.html', lab_bookings=lab_bookings,courses=courses,name=name,role = role)
    else:
        return render_template('profile.html',name=name,role =role)

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
            
    if request.method == 'GET':
        return render_template('login.html')
    
    return render_template('login.html')
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['reg_email']
        password = request.form['reg_password']
        role = request.form['role']
        name = request.form['name']

        # Insert new user into database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, name,password,role) VALUES (%s, %s, %s,%s)", (email, name,password,role))
        mysql.connection.commit()
        cur.close()

        # Redirect to login page after successful registration
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('register.html')

@app.route('/bookinglab')
def booking_lab():
    if 'loggedin' in session:
        role=fetch_role(session.get('email'))
        courses=fetch_courses()
        # print(role)
        return render_template('bookinglab.html', role=role,courses=courses)
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

def fetch_role(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE email = %s", (email,))
    role = cur.fetchone() 
    
    return role[0]

def fetch_courses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Course_ID FROM course")

    courses = cur.fetchall()  # Fetch all rows
    # print(courses)
    return courses

def fetch_student_courses(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Course_ID FROM student_enrolled WHERE email = %s", (email,))
    courses = cur.fetchall()  # Fetch all rows
    return courses

def fetch_prof_course(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Course_ID FROM course WHERE email = %s", (email,))
    courses = cur.fetchall()  # Fetch all rows
    return courses

def fetch_name(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name FROM users WHERE email = %s", (email,))
    name = cur.fetchone() 
    
    return name[0]


if __name__ == '__main__':       
    app.run(debug=True)


