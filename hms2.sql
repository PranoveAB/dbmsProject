DROP DATABASE IF EXISTS hms;
CREATE DATABASE hms;
USE hms;

-- create tables


CREATE TABLE MedicalRecord
(
    med_record_id INT PRIMARY KEY,
    Med_rec_des VARCHAR(1000) NOT NULL,
    allergy VARCHAR(100) NOT NULL,
    follow_up TIMESTAMP NOT NULL
);

insert into MedicalRecord values(1,'fever and sore throat','dust allergies','2023-01-01 10:30:00');

CREATE TABLE Hospital
(
    hosp_name VARCHAR(20) PRIMARY KEY,
    hosp_phone VARCHAR(10) NOT NULL,
    hosp_email VARCHAR(20) NOT NULL,
    fax VARCHAR(10) NOT NULL,
    hosp_address VARCHAR(50) NOT NULL
);

CREATE TABLE Payment
(
    payment_id INT PRIMARY KEY,
    payment_date DATE NOT NULL,
    payment_status VARCHAR(3) NOT NULL, -- yes/no
    payment_method VARCHAR(10) NOT NULL
);

CREATE TABLE MedicalInsurance
(
    insurance_id INT PRIMARY KEY,
    policy_no INT NOT NULL,
    company_name VARCHAR(20) NOT NULL,
    sum_insured FLOAT(6,2) NOT NULL,
    policy_start_date DATE NOT NULL,
    policy_end_date DATE NOT NULL
);

insert into MedicalInsurance values(1,123456,'ICICI',50000,'2022-01-01','2023-01-01');

CREATE TABLE Medication
(
    medicineId INT PRIMARY KEY,
    med_description VARCHAR(20) NOT NULL,
    dosage VARCHAR(10) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    duration VARCHAR(10) NOT NULL,
    refill INT NOT NULL,
    date_time_of_medication TIMESTAMP NOT NULL,
    med_cost FLOAT(6,2) NOT NULL
);

CREATE TABLE User
(
    userName VARCHAR(30) PRIMARY KEY,
    pwd varchar(10) NOT NULL,
    user_role varchar(10) NOT NULL
);

CREATE TABLE Address
(
	addr_id INT PRIMARY KEY,
    country VARCHAR(20) NOT NULL,
    state VARCHAR(20) NOT NULL,
    city VARCHAR(20) NOT NULL,
    street_name VARCHAR(20) NOT NULL,
    zip VARCHAR(5) NOT NULL
);

CREATE TABLE AdminStaff
(
    adminId INT PRIMARY KEY,
    admin_role VARCHAR(50) NOT NULL,
    email VARCHAR(30) NOT NULL,
    FOREIGN KEY (email)
    REFERENCES User(userName)
);

CREATE TABLE Doctor
(
    doc_id VARCHAR(10) PRIMARY KEY,
    specialization VARCHAR(20) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    email varchar(30) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    addr_id INT NOT NULL,
    joining_date DATE NOT NULL,
    dob DATE NOT NULL,
    sex CHAR(1) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    ssn varchar(9) NOT NULL,
    FOREIGN KEY (addr_id)
    REFERENCES Address(addr_id),
    FOREIGN KEY (email)
    REFERENCES User(userName)
);

CREATE TABLE Treatment
(
    treatmentId INT PRIMARY KEY,
    treat_name VARCHAR(10) NOT NULL,
    treat_description VARCHAR(50) NOT NULL,
    medicineId INT NOT NULL,
    FOREIGN KEY (medicineId)
    REFERENCES Medication(medicineId)
);

CREATE TABLE Diagnosis
(
    diagId INT PRIMARY KEY,
    diag_description VARCHAR(50) NOT NULL,
    treatmentId INT NOT NULL,
    FOREIGN KEY (treatmentId)
    REFERENCES Treatment(treatmentId),
    doc_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (doc_id)
    REFERENCES Doctor(doc_id)
);

CREATE TABLE Patient
(
    mrn INT PRIMARY KEY,
    patient_first_name VARCHAR(20) NOT NULL,
    patient_last_name VARCHAR(20) NOT NULL,
    patient_phone VARCHAR(10) NOT NULL,
    patient_email VARCHAR(20),
    patient_dob VARCHAR(10) NOT NULL,
    sex CHAR(1) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    addr_id INT NOT NULL,
    med_record_id INT NOT NULL,
    insurance_id INT NOT NULL,
    FOREIGN KEY (med_record_id)
    REFERENCES MedicalRecord(med_record_id),
    FOREIGN KEY (insurance_id)
    REFERENCES MedicalInsurance(insurance_id),
    FOREIGN KEY (addr_id)
    REFERENCES Address(addr_id),
    FOREIGN KEY (patient_email)
    REFERENCES User(userName)
);


insert into patient values
(
    1,
    'John',
    'Doe',
    '1234567890',
    "prathiksha@gmail.com",
    '1990-01-01',
    'F',
    'A+',
    3,
    1,
    1
);



CREATE TABLE Appointment
(
    app_id INT PRIMARY KEY,
    doc_id VARCHAR(10) NOT NULL,
    patient_id INT NOT NULL,
    date_time_app TIMESTAMP NOT NULL,
    FOREIGN KEY (patient_id)
    REFERENCES Patient(mrn),
    FOREIGN KEY (doc_id)
    REFERENCES Doctor(doc_id)
);

CREATE TABLE Bill
(
    bill_id INT PRIMARY KEY,
    bill_date DATE NOT NULL,
    total_cost FLOAT(6,2) NOT NULL
);

-- CREATE TABLE PatientDoctorAppointment
-- (
--     patient_id INT NOT NULL,
--     app_no INT NOT NULL,
--     doc_id VARCHAR(10) NOT NULL,
--     FOREIGN KEY (patient_id)
--     REFERENCES Patient(mrn),
--     FOREIGN KEY (app_no)
--     REFERENCES Appointment(app_id),
--     FOREIGN KEY (doc_id)
--     REFERENCES Doctor(doc_id)
-- );

CREATE TABLE PatientBill
(
    patient_num INT NOT NULL,
    FOREIGN KEY (patient_num)
    REFERENCES Patient(mrn),
    bill_no INT NOT NULL,
    FOREIGN KEY (bill_no)
    REFERENCES Bill(bill_id)
);

CREATE TABLE PatientPayment
(
    patient_no INT NOT NULL,
    payment_num INT NOT NULL,
    FOREIGN KEY (patient_no)
    REFERENCES Patient(mrn),
    FOREIGN KEY (payment_num)
    REFERENCES Payment(payment_id)
);


-- patient details include
