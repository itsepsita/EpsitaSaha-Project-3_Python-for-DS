from flask import Flask, render_template, request, redirect, session
import mysql.connector
import pickle
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="loan_db"
)
cursor = db.cursor()

# Load the model
with open('model/loan_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO User (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM User WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect('/enter_details')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        details = [
            request.form['Gender'],
            request.form['Married'],
            request.form['Dependents'],
            request.form['Education'],
            request.form['Self_Employed'],
            request.form['ApplicantIncome'],
            request.form['CoapplicantIncome'],
            request.form['LoanAmount'],
            request.form['Loan_Amount_Term'],
            request.form['Credit_History'],
            request.form['Property_Area']
        ]
        prediction = predict_loan_eligibility(details)
        return render_template('result.html', prediction=prediction)
    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# Prediction function
def predict_loan_eligibility(details):
    processed_details = np.array(details).reshape(1, -1)
    result = model.predict(processed_details)
    return "Eligible" if result[0] == 'Y' else "Not Eligible"

if __name__ == '__main__':
    app.run(debug=True)
