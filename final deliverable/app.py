# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import metrics


app = Flask(__name__)
model = pickle.load(open('model.pkl','rb'))

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'ibm-app'

mysql = MySQL(app)

@app.route('/')
@app.route('/home.html')
def initial():
    return render_template('/home.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM account WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('initial'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM account WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO account VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/input',methods=['GET','POST'])
def inp():
    return render_template('input.html')

@app.route('/home')
def home():
    return render_template('index.html')


@app.route("/predict",methods=['POST'])
def predicts():
    age = request.form["1"]
    Sex = request.form["2"]
    Chest_pain_type = request.form["3"]
    BP = request.form["4"]
    Cholesterol = request.form["5"]
    FBS = request.form["6"]
    EKG_results = request.form["7"]
    Max_HR = request.form["8"]
    Exercise_angina = request.form["9"]
    ST_depression = request.form["10"]
    Slope_of_ST = request.form["11"]
    Number_of_vessels_fluro = request.form["12"]
    Thallium = request.form["13"]
    t=[[int(age),int(Sex),int(Chest_pain_type),int(BP),int(Cholesterol),int(FBS),int(EKG_results),int(Max_HR),int(Exercise_angina),float(ST_depression),int(Slope_of_ST),int(Number_of_vessels_fluro),int(Thallium)]]
    print(t)
    print(type(model))
    output=model.predict(t)
    print(output)
    return render_template("predict.html",score = str(output[0]))

@app.route("/visualize_of_some_features_from_the_trained_dataset")
def visualize_of_some_features_from_the_trained_dataset():
    return render_template('visualize.html')

if __name__ == "__main__":
    app.run(debug=True)