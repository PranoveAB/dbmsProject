from flask import Flask, render_template, flash, redirect, url_for, session, request
import pymysql
from wtforms import Form, StringField,PasswordField, validators, DateTimeLocalField
from passlib.hash import sha256_crypt
from functools import wraps
from adminForms import AddPatientForm, AddDoctorForm, AddBillForm, AddPaymentForm, AddAdminForm
from doctorForm import AddMedicalRecord, AddTreatment, AddMedication, CreateAppointmentForm, InsuranceForm

app = Flask(__name__)

# Config MySQL

mysql = pymysql.connect(host='localhost',
                        user='root', 
                        password='Pranove*2',
                        db='finaldump',
                        cursorclass=pymysql.cursors.DictCursor
                        )

# Index
@app.route('/')
def index():
    return render_template('home.html')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = AddAdminForm(request.form)

    if request.method == 'POST':


        fname = form.firstName.data
        lname = form.lastName.data
        phone = form.phone.data
        dob = form.dateOfBirth.data
        sex = form.sex.data
        bloodGroup = form.bloodGroup.data
        ssn = form.ssn.data
        country = form.country.data
        state = form.state.data
        city = form.city.data
        street = form.streetName.data
        zipCode = form.zipCode.data
        username = form.email.data
        password = sha256_crypt.hash(str(form.password.data))
        userRole = 'admin'
        
        # Create cursor
        cur = mysql.cursor()
        cur.callproc('addAdmin', (fname, lname,phone, username,dob,sex,bloodGroup,ssn,country,state,city,street,zipCode,password,userRole))
    
        # Commit to DB
        mysql.commit()
        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
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
        result = cur.execute("SELECT * FROM user WHERE username = %s and user_role = %s" , [username, userRole])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            # print(data)
            password = data['pwd']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['user_role'] = userRole
            # Close connection
            cur.close()
            
            if session['user_role'] == 'doctor':
                return redirect(url_for('doctor'))
            elif session['user_role'] == 'patient':
                return redirect(url_for('patient'))
            elif session['user_role'] == 'admin':
                return redirect(url_for('admin'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

        else:
            error = 'User not found'
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
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Patient Dashboard

@app.route('/patient/<string:mrn>', methods=['GET', 'POST'])
@is_logged_in
def patientById(mrn):
    medicalRecord = AddMedicalRecord(request.form)
    treatment = AddTreatment(request.form)
    medication = AddMedication(request.form)
    patientBill = AddBillForm(request.form)
    patientPayment = AddPaymentForm(request.form)
    if request.method == 'POST':

        if(request.form.keys().__contains__('description')):
            description = medicalRecord.description.data
            allergies = medicalRecord.allergies.data 
            nextFollowUp = medicalRecord.nextFollowUp.data
            cur = mysql.cursor()
            cur.execute("update MedicalRecord set med_rec_des = %s, allergy = %s, follow_up = %s where med_record_id = (select med_record_id from patient where mrn = %s)", (description, allergies, nextFollowUp, mrn))
            mysql.commit()
            cur.close()
            flash('Medical Record Updated', 'success')
            return redirect(url_for('patientById', mrn = mrn))

        elif(request.form.keys().__contains__('diagnosis')):
            diagnosis = treatment.diagnosis.data
            treatmentName = treatment.treatmentName.data
            treatmentDescription = treatment.treatmentDescription.data
            cur = mysql.cursor()
            cur.execute("select * from diagnosisAndTreatment d join patient p on d.patient_mrn = p.mrn where p.mrn = %s", (mrn))
            data = cur.fetchone()
            if data is None:
                cur.execute("insert into diagnosisAndTreatment(treat_name, treat_desc, diag_desc, patient_mrn) values(%s, %s, %s, %s)", (treatmentName, treatmentDescription, diagnosis, mrn))
                mysql.commit()
            else:
                cur.execute("update diagnosisAndTreatment set treat_name = %s, treat_desc = %s, diag_desc = %s where patient_mrn = %s", (treatmentName, treatmentDescription, diagnosis, mrn))
                mysql.commit()
            cur.close()
            
            flash('Treatment Details Updated', 'success')
            return redirect(url_for('patientById', mrn = mrn))

        
        elif(request.form.keys().__contains__('medicationName')):
            medicationName = medication.medicationName.data
            medicationDosage = medication.medicationDosage.data
            medicationFrequency = medication.medicationFrequency.data
            medicationDuration = medication.medicationDuration.data
            medicationRefills = medication.refills.data
            medicationCost = medication.medicationCost.data

            # first check if the medication details are already present in the database
            # if yes, then update the details, else insert the details

            cur = mysql.cursor()
            cur.execute("select m.* from medication m join patient p on m.patient_mrn = p.mrn where p.mrn = %s", (mrn))
            data = cur.fetchone()
            if data is None:
                cur.execute("insert into medication(med_description,dosage, frequency, duration,refill, med_cost, patient_mrn) values(%s, %s, %s, %s, %s, %s, %s)", (medicationName, medicationDosage, medicationFrequency, medicationDuration, medicationRefills, medicationCost, mrn))
                mysql.commit()
                cur.close()
            else:
                cur.execute("update medication m join patient p on m.patient_mrn = p.mrn set med_description = %s, dosage = %s, frequency = %s, duration = %s, refill = %s, med_cost = %s where p.mrn  = %s", (medicationName, medicationDosage, medicationFrequency, medicationDuration, medicationRefills, medicationCost, mrn))
                mysql.commit()
                cur.close()
            flash('Medication Details Updated', 'success')
            return redirect(url_for('patientById', mrn = mrn))
        
        elif(request.form.keys().__contains__('billAmount')):
            billAmount = patientBill.billAmount.data
            billDate = patientBill.billDate.data
            print(billAmount, billDate)
            # first check if the bill details are already present in the database
            # if yes, then update the details, else insert the details
            cur = mysql.cursor()
            cur.execute("select * from bill where bill_id = (select bill_no from patientbill where patient_num = %s)", (mrn))
            data = cur.fetchone()
            if data is None:
                cur.callproc('AddPatientBill', (mrn, billDate, billAmount))
                mysql.commit()
                cur.close()
            else:
                cur.execute("update bill set total_cost = %s, bill_date = %s where bill_id = (select bill_no from patientbill where patient_num = %s)", (billAmount, billDate, mrn))
                mysql.commit()
                cur.close()

            flash('Bill Details Updated', 'success')
            return redirect(url_for('patientById', mrn = mrn))
        
        elif(request.form.keys().__contains__('paymentDate')):
            paymentDate = patientPayment.paymentDate.data
            paymentStatus = patientPayment.paymentStatus.data
            paymentMethod = patientPayment.paymentMethod.data

            # first check if the payment details are already present in the database for that bill id
            # if yes, then update the details, else insert the details
            cur = mysql.cursor()
            cur.execute("select * from payment where bill_id = (select bill_no from patientbill where patient_num = %s)", (mrn))
            data = cur.fetchone()
            if data is None:
                cur.execute("insert into payment(payment_date, payment_status, payment_method, bill_id) values(%s, %s, %s, (select bill_no from patientbill where patient_num = %s))", (paymentDate, paymentStatus, paymentMethod, mrn))
                mysql.commit()
                cur.close()
            else:
                cur.execute("update payment set payment_date = %s, payment_status = %s, payment_method = %s where bill_id = (select bill_no from patientbill where patient_num = %s)", (paymentDate, paymentStatus, paymentMethod, mrn))
                mysql.commit()
                cur.close()
            flash('Payment Details Updated', 'success')
            return redirect(url_for('patientById', mrn = mrn))

        return redirect(url_for('patientById', mrn=mrn))

    if session['user_role'] == 'doctor' or session['user_role'] == 'patient':
        cur = mysql.cursor()
        
        # A patient might not have an appointment yet
        cur.execute("select p.*,i.*,r.*,d.*, m.*, a.* from patient p join address a on p.addr_id=a.addr_id join MedicalInsurance i on p.insurance_id=i.insurance_id left join appointment app on p.mrn = app.patient_id left join MedicalRecord r on p.med_record_id = r.med_record_id left join diagnosisAndTreatment d on d.patient_mrn = p.mrn left join medication m on p.mrn = m.patient_mrn where p.mrn = %s", [mrn])
        
        patientData = cur.fetchone()
        cur.close()
        medicalRecord.description.data = patientData['Med_rec_des']
        medicalRecord.allergies.data = patientData['allergy']
        if patientData['follow_up'] is None:
            medicalRecord.nextFollowUp.data = ''
        medicalRecord.nextFollowUp.data = patientData['follow_up']
        treatment.diagnosis.data = patientData['diag_desc'] 
        treatment.treatmentName.data = patientData['treat_name']
        treatment.treatmentDescription.data = patientData['treat_desc']
        medication.medicationName.data = patientData['med_description']
        medication.medicationDosage.data = patientData['dosage']
        medication.medicationFrequency.data = patientData['frequency']
        medication.medicationDuration.data = patientData['duration']
        medication.refills.data = patientData['refill']
        medication.medicationCost.data = patientData['med_cost']
        
    if session['user_role'] == 'admin':
        cur = mysql.cursor()
        # cur.execute("select p.*,a.*,i.*,r.*,b.* from patient p join address a on p.addr_id=a.addr_id join bill b on (select bill_no from patientbill where patient_num = %s) join payment pay on pay.bill_id = b.bill_id join MedicalInsurance i on p.insurance_id=i.insurance_id join MedicalRecord r on p.med_record_id = r.med_record_id where p.mrn = %s", [mrn,mrn])
        cur.execute("select r.*,i.*,p.*, a.*, b.*, pay.* from patient p join address a on p.addr_id = a.addr_id join medicalInsurance i on p.insurance_id = i.insurance_id join medicalRecord r on p.med_record_id = r.med_record_id left join patientbill pb on p.mrn = pb.patient_num left join bill b on b.bill_id = pb.bill_no left join payment pay on pay.bill_id = b.bill_id where p.mrn = %s", [mrn])
        patientData = cur.fetchone()
        cur.close()

        patientBill.billDate.data= patientData['bill_date']
        patientBill.billAmount.data = patientData['total_cost']
        patientPayment.paymentDate.data = patientData['payment_date']
        patientPayment.paymentStatus.data = patientData['payment_status']
        patientPayment.paymentMethod.data = patientData['payment_method']

    return render_template('patient/patient.html',patientData=patientData, medicalRecord=medicalRecord, treatment=treatment, medication=medication,form=medicalRecord,patientBill=patientBill,patientPayment=patientPayment)
    

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

    # v1
    # cur.execute("select p.*,a.*,i.*,r.* from patient p join address a on p.addr_id=a.addr_id join MedicalInsurance i on p.insurance_id=i.insurance_id join MedicalRecord r on p.med_record_id = r.med_record_id join user u on p.patient_email = u.userName where u.userName = %s", [username])
    
    # patient might not have an appointment yet
    cur.execute("select p.*,a.*,i.*,r.*,d.*, m.*,b.*,pay.* from patient p join address a on p.addr_id=a.addr_id join MedicalInsurance i on p.insurance_id=i.insurance_id left join patientbill pb on p.mrn = pb.patient_num left join bill b on b.bill_id = pb.bill_no left join payment pay on pay.bill_id = b.bill_id left join appointment app on p.mrn = app.patient_id left join MedicalRecord r on p.med_record_id = r.med_record_id left join diagnosisAndTreatment d on d.patient_mrn = p.mrn left join medication m on p.mrn = m.patient_mrn join user u on p.patient_email = u.userName where u.userName = %s", [username])

    # v2
    # cur.execute("select p.*,a.*,i.*,r.*,d.*, m.* from patient p join address a on p.addr_id=a.addr_id join MedicalInsurance i on p.insurance_id=i.insurance_id join appointment app on p.mrn = app.patient_id join MedicalRecord r on p.med_record_id = r.med_record_id join diagnosisAndTreatment d on d.app_id = app.app_id join medication m on d.medicineId = m.medicineId join user u on p.patient_email = u.userName where u.userName = %s", [username])
    
    patientData = cur.fetchone()
    form1 = InsuranceForm(request.form)
    form1.policy_no.data = patientData['policy_no']
    form1.company_name.data = patientData['company_name']
    form1.sum_insured.data = patientData['sum_insured']
    form1.policy_start_date.data = patientData['policy_start_date']
    form1.policy_end_date.data = patientData['policy_end_date']
    cur = mysql.cursor()
    cur.execute(" select a.*, p.*, d.first_name, d.last_name from appointment a join patient p on a.patient_id = p.mrn join doctor d on d.doc_id = a.doc_id where p.patient_email = %s", [session['username']])
    appointmentData = cur.fetchall()
    events = []
    for row in appointmentData:
        events.append({
            'title': 'Dr.'+ row['first_name'] + ' ' + row['last_name'],
            'start': row['date_time_app'],
        })
    cur.close()
    return render_template('patient/patient.html',patientData = patientData, form = form1, events=events)


@app.route('/deleteAppointment', methods=['GET', 'POST'])
@is_logged_in
def deleteAppointment():
    if request.method == 'POST':
        # Get Form Fields
        appointment_id = request.form['appointment_id']
        # Create cursor
        cur = mysql.cursor()
        cur.execute("delete from appointment where appointment_id = %s", [appointment_id])
        # Commit to DB
        mysql.commit()
        # Close connection
        cur.close()
        flash('Appointment deleted', 'success')
        return redirect(url_for('patient'))

# Doctor Dashboard
@app.route('/doctor', methods=['GET', 'POST'])
@is_logged_in
def doctor():

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
    return render_template('doctor/doctor.html',data=data,addr=addr, events=events)

# Admin Dashboard
# works
@app.route('/admin')
@is_logged_in
def admin():

    cur = mysql.cursor()
    cur.execute(
       "select ad.*,a.* from adminstaff ad join address a on ad.addr_id = a.addr_id where ad.email = %s", [session['username']]
       )
    data = cur.fetchone()
    cur.close()

    # return "Admin Dashboard"
    return render_template('admin/admin.html',data=data)



# works
@app.route('/addPatient', methods=['GET', "POST"])
@is_logged_in
def addPatient():
    newPatient = AddPatientForm(request.form)
    if request.method == "POST":
        
        # Get Form Fields
        first_name = newPatient.firstName.data
        last_name = newPatient.lastName.data
        phoneNumber = newPatient.phoneNumber.data
        email = newPatient.email.data
        password = sha256_crypt.hash(str(newPatient.password.data))
        dob = newPatient.dateOfBirth.data
        sex = newPatient.sex.data
        bloodGroup = newPatient.bloodGroup.data
        streetName = newPatient.streetName.data
        city = newPatient.city.data
        state = newPatient.state.data
        country = newPatient.country.data
        zipcode = newPatient.zipCode.data
        medicalRecord = newPatient.medicalHistory.data
        allergies = newPatient.allergies.data
        policyNumber = newPatient.policyNumber.data
        policyProvider = newPatient.policyProvider.data
        sumInsured = newPatient.sumInsured.data
        policyStartDate = newPatient.policyStartDate.data
        policyEndDate = newPatient.policyEndDate.data
        userRole = 'patient'
        # Create cursor
        cur = mysql.cursor()
        cur.callproc('AddPatient', (first_name, last_name, phoneNumber, email, dob, sex,bloodGroup,country, state, city,streetName,zipcode,allergies,medicalRecord,policyNumber,policyProvider,sumInsured,policyStartDate,policyEndDate,password,userRole))
        mysql.commit()
        cur.close()

        flash('New Patient Added', 'success')
        return redirect(url_for('admin'))
    return render_template("admin/createPatient.html",form=newPatient)

# works
@app.route('/addDoctor', methods=['GET', "POST"])
@is_logged_in
def addDoctor():
    newDoctor = AddDoctorForm(request.form)
    if request.method == "POST":
        # Get Form Fields
        first_name = newDoctor.firstName.data
        last_name = newDoctor.lastName.data
        phoneNumber = newDoctor.phone.data
        email = newDoctor.email.data
        password = sha256_crypt.hash(newDoctor.password.data)
        dob = newDoctor.dateOfBirth.data
        sex = newDoctor.sex.data
        bloodGroup = newDoctor.bloodGroup.data
        streetName = newDoctor.streetName.data
        city = newDoctor.city.data
        state = newDoctor.state.data
        country = newDoctor.country.data
        zipcode = newDoctor.zipCode.data
        specialization = newDoctor.specialization.data
        ssn = newDoctor.ssn.data
        userRole = "doctor"
        joinDate = newDoctor.joiningDate.data
        
        cur = mysql.cursor()
        cur.callproc('AddDoctor', (specialization,first_name,last_name,email,phoneNumber,joinDate,dob,sex,bloodGroup,ssn,country,state,city,streetName,zipcode,password,userRole))
        mysql.commit()
        cur.close()
        flash('New Doctor Added', 'success')
        return redirect(url_for('admin'))

    return render_template("admin/createDoctor.html",form=newDoctor)

# works
@app.route('/add', methods=['GET', "POST"])
@is_logged_in
def add():
    appointmentform = CreateAppointmentForm(request.form)
    if request.method == "POST":
        appointmentDate = appointmentform.date_time.data
        doctorFirstName = appointmentform.doctorName.data.split()[0]
        doctorLastName = appointmentform.doctorName.data.split()[1]
        patientEmail = session['username']
        print(patientEmail, doctorFirstName, doctorLastName,appointmentDate)
        cur = mysql.cursor()
        cur.callproc('AddAppointment', (patientEmail, doctorFirstName, doctorLastName,appointmentDate ))
        mysql.commit()
        cur.close()
        flash('Appointment created', 'success')
        return redirect(url_for('patient'))
    return render_template("patient/createAppointment.html",form=appointmentform)

# works
@app.route('/listDoctors')
@is_logged_in
def listDoctors():
    cur = mysql.cursor()
    resultValue = cur.execute("select d.*, a.country, a.state, a.city, a.street_name, a.zip from doctor d join address a on d.addr_id = a.addr_id")
    doctors = cur.fetchall()
    cur.close()
    if resultValue > 0:
        return render_template('admin/doctors.html', doctors=doctors)
    else:
        msg = 'No Doctors Found'
        return render_template('admin/doctors.html', msg=msg)

# works
@app.route('/listPatients')
@is_logged_in
def listPatients():

    if session['user_role'] == 'doctor':
        cur = mysql.cursor()
        resultValue = cur.execute("select distinct p.*,a.* from patient p join address a on p.addr_id = a.addr_id join appointment ap on p.mrn = ap.patient_id where ap.doc_id = (select doc_id from doctor where email = %s)", [session['username']])
        patients = cur.fetchall()
        cur.close()
    elif session['user_role'] == 'admin':
        cur = mysql.cursor()
        resultValue = cur.execute("select p.*, a.country, a.state, a.city, a.street_name, a.zip from patient p join address a on p.addr_id = a.addr_id")
        patients = cur.fetchall()
        cur.close()

    if resultValue > 0:
        return render_template('admin/patients.html', patients=patients)
    else:
        msg = 'No Patients Found'
        return render_template('admin/patients.html', msg=msg)

# works
@app.route('/deletePatient/<string:id>', methods=['POST'])
@is_logged_in
def deletePatient(id):
    cur = mysql.cursor()
    cur.callproc('DeletePatient',[id])
    mysql.commit()
    cur.close()
    flash('Patient Deleted', 'success')
    return redirect(url_for('listPatients'))


# works
@app.route('/deleteDoctor/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def deleteDoctor(id):
    cur = mysql.cursor()
    cur.callproc('DeleteDoctor',[id])
    mysql.commit()
    cur.close()

    flash('Doctor Deleted', 'success')
    return redirect(url_for('listDoctors'))




if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)