from flask import Flask, render_template, request, redirect, url_for, session,json,jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = "brandon-litsurance"
 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'litsurance'
  
  
mysql = MySQL(app)
CORS(app)
 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 

def fetchData (table):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * ,count(customer_id) as 'count' FROM {table} ")
    account = cursor.fetchone()
    account['count'] = account['count'] if account['count'] > 0 else 0 
    return account['count'] 
    # return jsonify(account['count']) if account['count'] > 0  else  0


@app.route('/')
def main():
    return render_template('index.html');
    
@app.route('/login',methods =['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    data = fetchData(f"customers where customer_email = '{email}' and customer_password = '{password}' ")
    # print(data)
    return jsonify({"data":data})

 
@app.route('/upload', methods=['POST'])
def upload_data():
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    dob = request.form['dob']
    contact = request.form['contact']
    occupation = request.form['occupation']
    nature = request.form['nature']
    income = request.form['income']
    password = request.form['password']
    details = dict({"name":name ,"gender":gender ,"dob":dob,"email":email ,"contact":contact ,"occupation" : occupation ,"nature" : nature ,"income" : income ,"password":password})
    # check if the post request has the file part
    if 'files[]' not in request.files:  
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 200
        return resp
    
    files = request.files.getlist('files[]')
     
    errors = {}
    success = False
    i= 0 
    for file in files:      
        if file and allowed_file(file.filename):
            filename = secure_filename(details['name']+"_"+(file.filename))
            if i == 0 : details['aadhar'] = filename
            elif i == 1 : details['pan'] = filename
            else: details['itr'] = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
            i+=1
        else:
            errors[file.filename] = f'File type is not allowed for {file.filename}'
            success = False
            
    errors["data"]  = details
    if success:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO `customers`(`customer_name`, `customer_email`, `customer_contact`, `customer_dob`, `customer_gender`, `customer_occupation`, `customer_nature`, `customer_income`, `customer_aadhar`, `customer_pan`, `customer_itr`, `customer_password`) VALUES  ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s','%s')" % ((details['name']),(details['email']),(details['contact']),(details['dob']),(details['gender']),(details['occupation']),(details['nature']),(details['income']),(details['aadhar']),(details['pan']),(details['itr']),(details['password'])))
        mysql.connection.commit() 
        resp = jsonify({'message' : 'Files successfully uploaded',"data":details})
        resp.status_code = 200  
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
if __name__ == "__main__" :
   app.run(debug = False , host = "0.0.0.0")