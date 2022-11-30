from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL

mysql = pymysql.connect(host='localhost', user='root', password='Pranove*2', db='dbmsproj', cursorclass=pymysql.cursors.DictCursor)


# Index
@app.route('/')
def index():
    return render_template('home.html')

# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # name = form.name.data
        # email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        userRole = 'Patient'

        # Create cursor
        cur = mysql.cursor()

        # Execute query
        cur.execute("INSERT INTO user(userName, userPwd,userRole) VALUES(%s, %s, %s)", ( username, password, userRole))

        # Commit to DB
        mysql.commit()
        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for(''))
    return render_template('register.html', form=form)


# User login
@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        userRole = request.form['userRole']

        # Create cursor
        cur = mysql.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM user WHERE username = %s and userRole = %s" , [username, userRole])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['userPwd']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['userRole'] = userRole
            
            if session['userRole'] == 'doctor':
                return redirect(url_for('doctor'))
            elif session['userRole'] == 'patient':
                return redirect(url_for('patient'))
            elif session['userRole'] == 'admin':
                return redirect(url_for('admin'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

            # Close connection
            cur.close()
            
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('signin'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

class RegisterForm1(Form):
        policy_no = StringField('Policy No:', [validators.Length(min=4, max=25)],)
        company_name = StringField('Company Name:', [validators.Length(min=4, max=25)])
        sum_insured = StringField('Sum Insured:', [validators.Length(min=4, max=25)])
        policy_start_date = StringField('Policy Start Date:', [validators.Length(min=4, max=25)])
        policy_end_date = StringField('Policy End Date:', [validators.Length(min=4, max=25)])

# Patient Dashboard
@app.route('/patient', methods=['GET', 'POST'])
@is_logged_in
def patient():


    
    # get form fields from insurance div from patient dashboard to update insurance details
    if request.method == 'POST':
        # Get Form Fields
        policy_no = request.form['policy_no']
        company_name = request.form['company_name']
        sum_insured = request.form['sum_insured']
        policy_start_date = request.form['policy_start_date']
        policy_end_date = request.form['policy_end_date']
        
        # Create cursor
        cur = mysql.cursor()

        cur.execute("update medicalInsurance i join patient p on p.insurance_id = i.insurance_id set policy_no = %s, company_name = %s, sum_insured = %s, policy_start_date = %s, policy_end_date = %s where p.patient_email = %s", (policy_no, company_name, sum_insured, policy_start_date, policy_end_date, session['username']))

        # Commit to DB
        mysql.commit()
        # Close connection
        cur.close()
        
        flash('Insurance details updated', 'success')

        return redirect(url_for('patient'))


    #return "Patient Dashboard"
    username = session['username']
    # for each patient, get patient details, 
    cur = mysql.cursor()
    cur.execute("select p.*,a.*,i.*,r.* from patient p join address a on p.addr_id=a.addr_id join MedicalInsurance i on p.insurance_id=i.insurance_id join MedicalRecord r on p.med_record_id = r.med_record_id join user u on p.patient_email = u.userName where u.userName = %s", [username])
    patientData = cur.fetchone()
    form1 = RegisterForm1(request.form)
    form1.policy_no.data = patientData['policy_no']
    form1.company_name.data = patientData['company_name']
    form1.sum_insured.data = patientData['sum_insured']
    form1.policy_start_date.data = patientData['policy_start_date']
    form1.policy_end_date.data = patientData['policy_end_date']


    return render_template('patient.html',patientData = patientData, form = form1)


# Doctor Dashboard
@app.route('/doctor', methods=['GET', 'POST'])
@is_logged_in
def doctor():

    # events = [
    #     {
    #     'title': 'All Day Event',
    #     'start': '2022-11-01'
    #   },
    # {
    #     'title': 'Long Event',
    #     'start': '2022-11-07',
    #     'end': '2022-11-10',
    #     'color': 'purple',
    #     'id': '999'
    #   }
    # ]

    cur = mysql.cursor()
    cur.execute(
        " select a.*, p.*, d.first_name, d.last_name from appointment a join patient p on a.patient_id = p.mrn join doctor d on d.doc_id = a.doc_id where d.email = %s", [session['username']])
    appointmentData = cur.fetchall()
    events = []
    for row in appointmentData:
        events.append({
            'title': row['patient_first_name'] + ' ' + row['patient_last_name'],
            'start': row['date_time_app'],
            'color': 'purple'
        })
    
    print(events)


    cur.close()

    username = session['username']
    cur = mysql.cursor()
    cur.execute("SELECT * FROM doctor WHERE email = %s", [username])
    data = cur.fetchone()
    cur.close()
    cur = mysql.cursor()
    cur.execute("SELECT * FROM address WHERE addr_id = %s", [data['addr_id']])
    addr = cur.fetchone()
    cur.close()
    #return render_template('doctor.html')
    return render_template('doctor.html',data=data,addr=addr, events=events)

# Admin Dashboard

@app.route('/admin')
@is_logged_in
def admin():
    # return "Admin Dashboard"
    username = session['username']

    return render_template('admin.html',username=username)



# # Dashboard
# @app.route('/dashboard')
# @is_logged_in
# def dashboard():
#     # Create cursor
#     cur = mysql.cursor()

#     # Get articles
#     #result = cur.execute("SELECT * FROM articles")
#     # Show articles only from the user logged in 
#     result = cur.execute("SELECT * FROM user WHERE userName = %s", [session['username']])
#     data = cur.fetchone()
#     return data







if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)