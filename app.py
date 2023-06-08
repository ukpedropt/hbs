from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

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
        
        # Create a new User instance
        user = User(username=username, email=email, password=password)
        
        # Add the user to the database
        db.session.add(user)
        db.session.commit()
        
        # Redirect to a success page or another route
        return redirect(url_for('success'))
    
    return render_template('register.html')

@app.route('/success')
def success():
    return 'Registration successful!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the tables
    app.run(debug=True)
