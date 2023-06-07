from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', message='Welcome to the Hotel Booking App!')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Process the form data (e.g., store in database, etc.)
        # Add your code here
        
        # Redirect to a success page or another route
        return redirect(url_for('success'))
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
