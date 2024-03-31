from flask import Flask, render_template, request, redirect,session, url_for
# from Flask-MySQLdb import MySQL
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import redirect
import os

# app = Flask(__name__,  template_folder='C:/Users/anish/Desktop/Frontend_Lab/DBMS_frontend/src')

# Get the absolute path of the directory where this file is located
# dir_path = os.path.dirname(os.path.realpath(__file__))

# app = Flask(__name__, template_folder=dir_path)
app = Flask(__name__)

# Configure MySQL
app.secret_key = 'abcd2123445'  
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lab_bookings'

mysql = MySQL(app)

session_email=None
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
        
    if request.method == 'POST':
        details = request.form
        email = session.get('email')  # Retrieve email from session
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE Email_ID = %s", (email,))
        user = cur.fetchone()
        if user==None:
            cur.execute("SELECT * FROM professor WHERE Email_ID = %s", (email,))
            user = cur.fetchone()
            if user==None:
                cur.execute("SELECT * FROM staff WHERE Email_ID = %s", (email,))
                user = cur.fetchone()
        if user:
            name=user[1]
        # Check if the form is for lab booking or equipment issuing
        if 'lab_name' in details:
                # Lab booking form data
                lab_name = details['lab_name']
                time_slot = details['time_slot']
                date= details['date']
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM bookings WHERE lab_name = %s AND date = %s AND time_slot = %s", (lab_name, date, time_slot))
                existing_booking = cur.fetchone()
                if existing_booking:
                    return redirect(url_for('booking_lab'))
                else:
                    cur.execute("INSERT INTO bookings (user_email, name, lab_name, time_slot, date) VALUES (%s, %s, %s, %s, %s)", (email, name, lab_name, time_slot, date))
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
            # request.form.getlist('Enrolled_Course_ID')
            enrolled_course_ids = request.form.getlist('Enrolled_Course_ID')
            cur = mysql.connection.cursor()
            cur.execute("SELECT Roll_Number FROM students WHERE Email_ID = %s", (email,))
            roll_no = cur.fetchone()[0]
            for enrolled_course in enrolled_course_ids:
                print(enrolled_course[2:-3])
                cur.execute("SELECT * FROM student_enrolled WHERE Course_Id = %s AND Roll_Number = %s", (enrolled_course[2:-3], roll_no))
                user = cur.fetchone()
                if user:
                    continue
                cur.execute("INSERT INTO student_enrolled (Course_Id, Roll_Number) VALUES (%s, %s)", (enrolled_course[2:-3], roll_no))  
                mysql.connection.commit()
            
            cur.close()


                
          
        elif 'Course_Name' in details:
            # print("Hello")
            course_name= details['Course_Name']
            course_id= details['Course_ID']
            credits= details['Credits']
            
            cur = mysql.connection.cursor()
            cur.execute("select * from professor where Email_ID = %s", (email,))
            user = cur.fetchone()
            employee_id=user[0]
            cur.execute("INSERT INTO course (Course_ID, Course_Name, Credits) VALUES (%s, %s, %s)", (course_id,course_name, credits))
            mysql.connection.commit()
            cur.execute("INSERT INTO instructor(Course_ID, Employee_ID) VALUES (%s, %s)", (course_id,employee_id))
            # cur.execute("INSERT INTO course (email,Course_ID, Course_Name, Credits) VALUES (%s,%s, %s, %s)", (email,course_id,course_name, credits))
            mysql.connection.commit()    
            cur.close()
                
        else:
                # Equipment issuing form data
                equipmentID = details['equipmentID']
                # number_of_equipment = details['numberOfEquipment']
                issue_date = details['issueDate']
                return_date = details['returnDate']
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT ID,isAvailable FROM inventory WHERE ID = %s", (equipmentID,))
                existing_id = cur.fetchone()
                if not existing_id:
                    return redirect(url_for('booking_lab'))
                elif (existing_id[1]==0):
                    return redirect(url_for('booking_lab'))
                cur.execute("INSERT INTO EquipmentIssued (user_email, equipmentID, issue_date, return_date) VALUES (%s, %s, %s, %s)", (email, equipmentID, issue_date, return_date))
                mysql.connection.commit()
                cur.execute("UPDATE inventory SET isAvailable = 0 WHERE ID = %s", (equipmentID,))
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
        # session_email=email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch user from database
        # cur = mysql.connection.cursor()
        cursor.execute("SELECT * FROM students WHERE Email_ID = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user==None:
            cursor.execute("SELECT * FROM professor WHERE Email_ID = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            if user==None:
                cursor.execute("SELECT * FROM staff WHERE Email_ID = %s AND password = %s", (email, password))
                user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['email'] = user['Email_ID']
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
        first_name=request.form['first name']
        last_name=request.form['last name']
        middle_name = request.form['middle name']
        roll_no = request.form['roll number']
        lab_name = request.form['Lab name']
        # print(role)
        # Insert new user into database
        cur = mysql.connection.cursor()
        if(role=='student'):
             cur.execute("INSERT INTO students (Roll_Number, First_Name, Middle_Name, Last_Name, Email_ID, password) VALUES (%s, %s, %s,%s,%s,%s)", (roll_no, first_name,middle_name,last_name,email,password))
            #  cur.execute("INSERT INTO students (Email_ID, First_Name,password) VALUES (%s, %s, %s,%s)", (email, name,password,role))
        elif(role=='professor'):
            cur.execute("INSERT INTO professor (Employee_ID,Email_ID, First_Name, Middle_Name, Last_Name,  password) VALUES (%s,%s, %s, %s,%s,%s)", (roll_no, email, first_name,middle_name,last_name,password))
            # cur.execute("INSERT INTO professors (Email_ID, First_Name,password) VALUES (%s, %s, %s,%s)", (email, name,password,role))
        elif(role=='staff'):
            cur.execute("INSERT INTO staff (Employee_ID,Email_ID, First_Name, Middle_Name, Last_Name, password,Lab_Name) VALUES (%s,%s, %s, %s,%s,%s,%s)", (roll_no, email, first_name,middle_name,last_name,password,lab_name))
            # cur.execute("INSERT INTO staff (email, name,password) VALUES (%s, %s, %s,%s)", (email, name,password,role))
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
    cur.execute("SELECT * FROM students WHERE Email_ID = %s", (email,))
    role = cur.fetchone() 
    if(role==None):
        cur.execute("SELECT * FROM professor WHERE Email_ID = %s", (email,))
        role = cur.fetchone() 
        if(role==None):
            cur.execute("SELECT * FROM staff WHERE Email_ID = %s", (email,))
            role = 'staff'
        else:
            role = 'professor'
    else:
        role = 'student'
    return role

def fetch_courses():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Course_ID FROM course")

    courses = cur.fetchall()  # Fetch all rows
    # print(courses)
    return courses

def fetch_student_courses(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students WHERE Email_ID = %s", (email,))
    roll_no = cur.fetchone()
    roll_no=roll_no[0]
    cur.execute("SELECT Course_ID FROM student_enrolled WHERE Roll_Number = %s", (roll_no,))
    courses = cur.fetchall()  # Fetch all rows
    return courses

def fetch_prof_course(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM professor WHERE Email_ID = %s", (email,))
    emp_id = cur.fetchone()
    emp_id=emp_id[0]
    cur.execute("SELECT Course_ID FROM instructor WHERE Employee_ID = %s", (emp_id,))
    courses = cur.fetchall()  # Fetch all rows
    return courses

def fetch_name(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT First_Name FROM students WHERE Email_ID = %s", (email,))
    name = cur.fetchone() 
    if(name==None):
        cur.execute("SELECT First_Name FROM professor WHERE Email_ID = %s", (email,))
        name = cur.fetchone() 
        if(name==None):
            cur.execute("SELECT First_Name FROM staff WHERE Email_ID = %s", (email,))
            name = cur.fetchone()
    return name[0]


if __name__ == '__main__':       
    app.run(debug=True)


