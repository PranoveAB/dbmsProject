from wtforms import Form, StringField, validators, IntegerField, TextAreaField, DateField


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