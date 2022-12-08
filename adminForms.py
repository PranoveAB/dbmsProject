

from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FloatField, DateField, IntegerField


class AddPatientForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=200),validators.DataRequired()])
    lastName = StringField('Last Name', [validators.Length(min=1, max=200),validators.DataRequired()])
    phoneNumber = StringField('Phone Number', [validators.Length(min=1, max=200),validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1, max=200),validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=8, max=15),validators.DataRequired()])
    dateOfBirth = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired()])
    sex = StringField('Sex', [validators.Length(min=1, max=200)])
    bloodGroup = StringField('Blood Group', [validators.Length(min=1, max=200)])
    city = StringField('City', [validators.Length(min=1, max=200)])
    streetName = StringField('Street Name', [validators.Length(min=1, max=200)])
    state = StringField('State', [validators.Length(min=1, max=200)])
    country = StringField('Country', [validators.Length(min=1, max=200)])
    zipCode = IntegerField('Zip Code', [validators.Length(min=1, max=200)])
    medicalHistory = TextAreaField('Medical History', [validators.Length(min=1, max=2000)])
    allergies = TextAreaField('Allergies', [validators.Length(min=1, max=200)])
    policyNumber = StringField('Policy Number', [validators.Length(min=1, max=200)])
    policyProvider = StringField('Policy Provider', [validators.Length(min=1, max=200)])
    sumInsured = IntegerField('Sum Insured', [validators.Length(min=1, max=200)])
    policyStartDate = DateField('Policy Start Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    policyEndDate = DateField('Policy End Date', format='%Y-%m-%d', validators=[validators.DataRequired()])

class AddDoctorForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=200)])
    lastName = StringField('Last Name', [validators.Length(min=1, max=200)])
    dateOfBirth = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired()])
    sex = StringField('Sex', [validators.Length(min=1, max=200)])
    city = StringField('City', [validators.Length(min=1, max=200)])
    streetName = StringField('Street Name', [validators.Length(min=1, max=200)])
    state = StringField('State', [validators.Length(min=1, max=200)])
    country = StringField('Country', [validators.Length(min=1, max=200)])
    zipCode = IntegerField('Zip Code', [validators.Length(min=1, max=200)])
    phone = StringField('Phone', [validators.Length(min=1, max=20)])
    email = StringField('Email', [validators.Length(min=1, max=200)])
    joiningDate = DateField('Joining Date',  format='%Y-%m-%d', validators=[validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=8, max=15),validators.DataRequired()])
    specialization = StringField('Specialization', [validators.Length(min=1, max=200)])
    bloodGroup = StringField('Blood Group', [validators.Length(min=1, max=10)])
    ssn = StringField('SSN', [validators.Length(min=1, max=20)])


class AddBillForm(Form):
    billDate = DateField('Bill Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    billAmount = FloatField('Bill Amount', [validators.NumberRange(min=0, max=100000)])

class AddPaymentForm(Form):
    paymentDate = DateField('Payment Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    paymentStatus = StringField('Payment Status', [validators.Length(min=1, max=200)])
    paymentMethod = StringField('Payment Method', [validators.Length(min=1, max=200)])