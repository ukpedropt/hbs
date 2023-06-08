from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database initialization
db.init_app(app)
with app.app_context():
    db.create_all()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', message='Welcome to the Hotel Booking App!')

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Generate password hash
        password_hash = generate_password_hash(password)
        
        # Create a new User instance with the hashed password
        user = User(username=username, email=email, password=password_hash)
        
        # Add the user to the database
        db.session.add(user)
        db.session.commit()
        
        # Redirect to the login page
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('success'))
        
        return 'Invalid username or password'
    
    return render_template('login.html')


@app.route('/success')
@login_required
def success():
    return f'Welcome, {current_user.username}!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
