from flask import Flask, render_template, request
import pandas as pd
import pickle
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the pre-trained model
with open('model.pkl', 'rb') as file:
    nb = pickle.load(file)

# Define a mapping from string values to integer values
mapping = {'Yes': 2, 'No': 0, 'Sometimes': 1}

# Define a function to preprocess the input data
def preprocess_input(q1, q2, q3, q4, q5, q6, q7, q8):
    # Create a pandas DataFrame with the input values
    input_data = pd.DataFrame({'q1': [q1], 'q2': [q2], 'q3': [q3], 'q4': [q4], 'q5': [q5], 'q6': [q6], 'q7': [q7], 'q8': [q8]})
    
    # Apply the mapping to the input values
    input_data = input_data.applymap(lambda x: mapping.get(x, x))
    
    return input_data

# Define a function to make a prediction using the pre-trained model
def predict(input_data):
    # Make a classification using the Naive Bayes algorithm
    prediction = nb.predict(input_data)
    
    # Map the integer prediction to the corresponding word
    if prediction[0] == 0:
        prediction_word = 'less addictive to alcohol'
    elif prediction[0] == 1:
        prediction_word = 'mildly addictive to alcohol'
    else:
        prediction_word = 'high addiction to alcohol'
    
    return prediction_word

# Define a route for the home page
@app.route('/')
def home():
    return render_template('home.html')

import random
import string

def generate_serial(length=8):
    # Define the character set for the serial code
    charset = string.ascii_uppercase + string.digits
    
    # Generate a random string of characters from the character set
    serial = ''.join(random.choice(charset) for i in range(length))
    
    return serial

# Define a route for the prediction page
@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    if request.method == 'POST':
        # Get the input values from the form
        name = request.form['name']
        birthday = request.form['birthday']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form['address']
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        q6 = request.form['q6']
        q7 = request.form['q7']
        q8 = request.form['q8']

        # Generate a random serial code
        code = generate_serial()

        # Preprocess the input data
        input_data = preprocess_input(q1, q2, q3, q4, q5, q6, q7, q8)
        
        # Make a prediction using the pre-trained model
        prediction = predict(input_data)
        
        # Save the input data and prediction to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO predictions (name, birthday, age, gender, contact, address, code, q1, q2, q3, q4, q5, q6, q7, q8, prediction) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, birthday, age, gender, contact, address, code, q1, q2, q3, q4, q5, q6, q7, q8, prediction))
        conn.commit()
        conn.close()
        
        # Render the prediction page with the result
        return render_template('results.html', prediction=prediction, name=name, birthday=birthday, age=age, gender=gender, contact=contact, address=address, code=code, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7, q8=q8)
    else:
        return render_template('predict.html')
    
def create_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE predictions
                (id INTEGER PRIMARY KEY,
                name TEXT,
                birthday TEXT,
                age INTEGER,
                gender TEXT,
                contact TEXT,
                address TEXT,
                code TEXT UNIQUE,
                q1 TEXT,
                q2 TEXT,
                q3 TEXT,
                q4 TEXT,
                q5 TEXT,
                q6 TEXT,
                q7 TEXT,
                q8 TEXT,
                prediction TEXT)''')
    
    conn.commit()
    conn.close()

# Define a route for the history page
@app.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        # handle form submission
        pass
    else:
        # retrieve all predictions from the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions")
        predictions = cursor.fetchall()
        conn.close()
        
        # filter predictions by search query (if provided)
        search_query = request.args.get('search_query')
        if search_query:
            search_query = search_query.strip()
            if len(search_query) > 0:
                predictions = [p for p in predictions if search_query.lower() in p[1].lower() or search_query.lower() in p[7].lower()]

        return render_template('history.html', predictions=predictions)

@app.route('/search', methods=['GET'])
def search_predictions():
    # redirect to the history page with the search query as a parameter
    search_query = request.args.get('search_query')
    return redirect(url_for('history', search_query=search_query))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM predictions WHERE id = ?', (id,))
    prediction = cur.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form['address']
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        q6 = request.form['q6']
        q7 = request.form['q7']
        q8 = request.form['q8']
        
        # Preprocess the input data
        input_data = preprocess_input(q1, q2, q3, q4, q5, q6, q7, q8)
        
        # Make a prediction using the pre-trained model
        prediction = predict(input_data)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('''UPDATE predictions SET name=?, birthday=?, age=?, gender=?, contact=?, address=?, q1=?, q2=?, q3=?, q4=?, q5=?, q6=?, q7=?, q8=?, prediction=? WHERE id=?''',
                    (name, birthday, age, gender, contact, address, q1, q2, q3, q4, q5, q6, q7, q8, prediction, id))
        conn.commit()
        conn.close()

        flash('Prediction updated successfully!')
        return redirect(url_for('history'))

    return render_template('update.html', prediction=prediction)

@app.route('/delete/<string:id>')
def delete_prediction(id):
    # Check if the record exists
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (id,))
    record = cursor.fetchone()
    conn.close()

    if not record:
        return render_template('not_found.html')

    # Delete the record
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (id,))
    rows_deleted = cursor.rowcount # Add this line
    conn.commit()
    conn.close()

    # Check if the query executed without errors
    if rows_deleted == 0:
        return render_template('error.html')

    # Redirect to the history page
    return redirect(url_for('history'))

@app.route('/view/<int:id>', methods=['GET'])
def view(id):
    # retrieve the selected prediction from the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (id,))
    prediction = cursor.fetchone()
    conn.close()

    # check if the prediction exists
    if not prediction:
        flash('Prediction not found.', 'error')
        return redirect(url_for('history'))

    # extract the fields we want to display
    name = prediction[1]
    birthday = prediction[2]
    age = prediction[3]
    gender = prediction[4]
    contact = prediction[5]
    address = prediction[6]
    code = prediction[7]
    q1 = prediction[8]
    q2 = prediction[9]
    q3 = prediction[10]
    q4 = prediction[11]
    q5 = prediction[12]
    q6 = prediction[13]
    q7 = prediction[14]
    q8 = prediction[15]
    predictions = prediction[16]

    # pass the data to the view.html template
    return render_template('view.html', predictions=predictions, name=name, birthday=birthday, age=age, gender=gender, contact=contact, address=address, code=code, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7, q8=q8)


if __name__ == '__main__':
    app.run(debug=True)


