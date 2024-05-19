# app.py
import csv
import json
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import pandas as pd

app = Flask(__name__)
app.secret_key = 'Ch@r@n24'


# MySQL Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Ch@r@n24'
MYSQL_DB = 'final_project'

# Connect to MySQL
conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, cursorclass=pymysql.cursors.DictCursor)
# Load the CSV file once into a DataFrame
df = pd.read_csv('open_food_facts.csv')


# Route for home page
@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_results = search_names(search_query)
        search_results = json.loads(search_results)
        return render_template('home.html', search_results=search_results)
    return render_template('home.html', search_results=None)
# Function to search names in the DataFrame
def search_names(query):
    results = df[df['product_name'].str.contains(query, case=False) | df['brands'].str.contains(query, case=False)]['product_name']
    json_data = results.to_json(orient='index', force_ascii=False)
    return json_data


    
    
# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username and password match the database
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Store user data in session
            session['user_id'] = user['id']
            session['username'] = user['username']
            # If user exists, redirect to home page
            return redirect(url_for('home'))
        else:
            # If user does not exist, redirect to login page with error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        health_conditions = request.form['health_conditions']
        allergies = request.form['allergies']
        
        # Check if username already exists in the database
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # If username already exists, redirect to registration page with error message
            return render_template('register.html', error='Username already exists')
        else:
            # If username does not exist, insert new user into the database
            cursor.execute(
                'INSERT INTO users (username, password, age, gender, height, weight, health_conditions, allergies) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (username, password, age, gender, height, weight, health_conditions, allergies)
            )
            conn.commit()
            cursor.close()
            # Redirect to login page after successful registration
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        # Update user details in the database
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        health_conditions = request.form['health_conditions']
        allergies = request.form['allergies']
        height = request.form['height']
        weight = request.form['weight']
        
        cursor.execute(
            'UPDATE users SET username = %s, password = %s, age = %s, gender = %s, health_conditions = %s, allergies = %s, height = %s, weight = %s WHERE id = %s',
            (username, password, age, gender, health_conditions, allergies, height, weight, user_id)
        )
        conn.commit()
        cursor.close()
        
        # Update session user data if username was changed
        session['username'] = username
        
        # Redirect to home page after updating profile
        return redirect(url_for('home'))
    
    cursor.close()
    
    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
