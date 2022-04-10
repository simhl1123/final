from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/insertEmp", methods=['POST'])
def insertEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    Payscale = request.form['Payscale']
    Department = request.form['Department']
    Hire_Date = request.form['Hire_Date']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employees1 VALUES (%s, %s, %s, %s, %s)"                     #CHANGE NAME
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, Payscale, Department, Hire_Date))
        db_conn.commit()
        empl_id = "" + emp_id 
        emp_name = "" + first_name 
        emp_Payscale = "" + Payscale 
        emp_Department = "" + Department 
        emp_Hire_Date = "" + Hire_Date 
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + ".jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('InsertEmpOutput.html', id=empl_id, name=emp_name, Payscale=emp_Payscale, Department=emp_Department, Date=emp_Hire_Date)


@app.route("/InsertEmpPage", methods=['GET', 'POST'])
def InsertEmpPage():
    return render_template('InsertEmp.html')

@app.route("/getInfo", methods=['GET', 'POST'])
def getInfo():
    return render_template('GetEmp.html')

@app.route("/fetchInfo", methods=['GET','POST'])
def fetchInfo():
    ID = request.form['emp_id']
    mycursor = db_conn.cursor()

    emp_id = "N/A"
    emp_name = "N/A"
    emp_payscale = "N/A"
    emp_department = "N/A"
    emp_hire_date = "N/A"
    emp_image = None
    
    try:
        mycursor.execute("SELECT * FROM employees WHERE emp_id = %s",[ID])

        myresult = mycursor.fetchall()
        for row in myresult:
            emp_id = row[0]
            emp_name = row[1]
            emp_payscale = row[2]
            emp_department = row[3]
            emp_hire_date = row[4]
            
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + ".jpg"
        
        s3_image_url = "https://ongzhenghao-bucket.s3.amazonaws.com/" + emp_image_file_name_in_s3

        return render_template('GetEmpOutput.html',image=s3_image_url, id=emp_id, name=emp_name, payscale=emp_payscale, department=emp_department, hire_date=emp_hire_date)
    
    except Exception as e:
        
        return render_template('GetEmpOutput.html',image=emp_image, id=emp_id, name=emp_name, payscale=emp_payscale, department=emp_department, hire_date=emp_hire_date)

    finally:
        mycursor.close()


@app.route("/markAttend", methods=['GET', 'POST'])
def markAttend():
    mycursor = db_conn.cursor()

    
    mycursor.execute("SELECT * FROM employees")
    myresult = mycursor.fetchall()

    
    return render_template('Attendence.html',emplist=myresult)

@app.route("/mark", methods=['GET', 'POST'])
def mark():
    mycursor = db_conn.cursor()
    i = 0
    emp_id=""
    emp_name=""
    emp_department=""
    attendlist = request.form.getlist('attend')
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    
    mycursor.execute("SELECT * FROM employees")
    
    myresult = mycursor.fetchall()
    
    
    insert_sql = "INSERT INTO attendence VALUES (%s, %s, %s, %s, %s)"  

    for emplist in myresult:
        emp_id = emplist[0]
        emp_name = emplist[1]
        emp_department = emplist[3]
        emp_attend = attendlist[i]

        mycursor.execute(insert_sql, (emp_id, emp_name, emp_department,emp_attend,date_time_str))
        i=i+1
    
    db_conn.commit()

    return render_template('Home.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)