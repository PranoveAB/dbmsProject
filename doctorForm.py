from wtforms import Form, StringField, validators, IntegerField, TextAreaField, DateField, DateTimeLocalField


class AddMedicalRecord(Form):
    description = TextAreaField('Description', [validators.Length(min=1, max=500)])
    allergies = TextAreaField('Allergies', [validators.Length(min=1, max=500)])
    nextFollowUp = DateField('Next Follow Up', format='%Y-%m-%d')

class AddTreatment(Form):
    treatmentName = StringField('Treatment Name', [validators.Length(min=1, max=50)])
    treatmentDescription = TextAreaField('Treatment Description', [validators.Length(min=1, max=500)])
    diagnosis = TextAreaField('Diagnosis', [validators.Length(min=1, max=500)])

class AddMedication(Form):
    medicationName = StringField('Medication Name', [validators.Length(min=1, max=50)])
    medicationDosage = StringField('Medication Dosage', [validators.Length(min=1, max=50)])
    medicationFrequency = StringField('Medication Frequency', [validators.Length(min=1, max=50)])
    medicationDuration = StringField('Medication Duration', [validators.Length(min=1, max=50)])
    refills = IntegerField('Refills', [validators.NumberRange(min=0, max=10)])
    medicationCost = IntegerField('Medication Cost', [validators.NumberRange(min=0, max=100000)])

# works
class CreateAppointmentForm(Form):
    date_time = DateTimeLocalField('Appointment Date and Time:', format='%Y-%m-%dT%H:%M')
    doctorName = StringField('Doctor First and Last Name:', [validators.Length(min=4, max=25)])

class InsuranceForm(Form):
    policy_no = StringField('Policy No:', [validators.Length(min=4, max=25)],)
    company_name = StringField('Company Name:', [validators.Length(min=4, max=25)])
    sum_insured = StringField('Sum Insured:', [validators.Length(min=4, max=25)])
    policy_start_date = StringField('Policy Start Date:', [validators.Length(min=4, max=25)])
    policy_end_date = StringField('Policy End Date:', [validators.Length(min=4, max=25)])