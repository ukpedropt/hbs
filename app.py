import os
import time
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize database migrations
migrate = Migrate(app, db)

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

# Define Amenity model
class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Define Hotel model
class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)

    amenities = db.relationship('Amenity', secondary='hotel_amenities', backref=db.backref('hotels', lazy='dynamic'))
    rooms = db.relationship('Room', backref='hotel', lazy='dynamic')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

# Define Hotel-Amenity association table
hotel_amenities = db.Table('hotel_amenities',
    db.Column('hotel_id', db.Integer, db.ForeignKey('hotel.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True)
)

# Define Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)

# Configure user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define user roles and required permissions
USER_ROLES = {
    'admin': ['create', 'read', 'update', 'delete'],
    'user': ['read']
}

# Decorator to check role-based permissions
def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Homepage route
@app.route('/')
def index():
    return render_template('index.html', message='Welcome to the Hotel Booking App!')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))  # Redirect to the homepage
        return 'Invalid username or password'
    return render_template('login.html')

# Login success route (requires login)
@app.route('/login_success')
@login_required
def login_success():
    return render_template('login_success.html', username=current_user.username)

# User success route (requires login)
@app.route('/success')
@login_required
def success():
    return render_template('success.html', username=current_user.username)

# User logout route (requires login)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

# Admin dashboard route (requires login and admin role)
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    hotels = Hotel.query.all()
    amenities = Amenity.query.all()
    users = User.query.all()
    return render_template('admin_dashboard.html', hotels=hotels, amenities=amenities, users=users)



# Create sample hotels, rooms, and amenities
@app.route('/create_sample_data')
def create_sample_data():
    # Create amenities
    amenity1 = Amenity(name='Free Wi-Fi')
    amenity2 = Amenity(name='Swimming Pool')
    amenity3 = Amenity(name='Gym')
    db.session.add_all([amenity1, amenity2, amenity3])
    db.session.commit()

    # Create hotels
    hotel1 = Hotel(name='Hotel A', description='This is Hotel A', location='Location A', room_type='Single')
    hotel2 = Hotel(name='Hotel B', description='This is Hotel B', location='Location B', room_type='Double')
    hotel3 = Hotel(name='Hotel C', description='This is Hotel C', location='Location C', room_type='Single')
    hotel4 = Hotel(name='Hotel D', description='This is Hotel D', location='Location D', room_type='Double')
    db.session.add_all([hotel1, hotel2, hotel3, hotel4])
    db.session.commit()

    # Create rooms for Hotel A
    room1 = Room(number='101', price=100.0, hotel=hotel1)
    room2 = Room(number='102', price=150.0, hotel=hotel1)
    room3 = Room(number='103', price=120.0, hotel=hotel1)
    room4 = Room(number='104', price=180.0, hotel=hotel1)
    db.session.add_all([room1, room2, room3, room4])

    # Create rooms for Hotel B
    room5 = Room(number='201', price=200.0, hotel=hotel2)
    room6 = Room(number='202', price=250.0, hotel=hotel2)
    room7 = Room(number='203', price=220.0, hotel=hotel2)
    room8 = Room(number='204', price=280.0, hotel=hotel2)
    db.session.add_all([room5, room6, room7, room8])

    # Create rooms for Hotel C
    room9 = Room(number='301', price=100.0, hotel=hotel3)
    room10 = Room(number='302', price=150.0, hotel=hotel3)
    room11 = Room(number='303', price=120.0, hotel=hotel3)
    room12 = Room(number='304', price=180.0, hotel=hotel3)
    db.session.add_all([room9, room10, room11, room12])

    # Create rooms for Hotel D
    room13 = Room(number='401', price=200.0, hotel=hotel4)
    room14 = Room(number='402', price=250.0, hotel=hotel4)
    room15 = Room(number='403', price=220.0, hotel=hotel4)
    room16 = Room(number='404', price=280.0, hotel=hotel4)
    db.session.add_all([room13, room14, room15, room16])

    db.session.commit()

    return redirect(url_for('admin_dashboard'))

# Hotels route
@app.route('/hotels')
def hotels():
    hotels = Hotel.query.all()
    return render_template('hotels.html', hotels=hotels)

# Hotel details route
@app.route('/hotels/<int:hotel_id>')
def hotel_details(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    return render_template('hotel_details.html', hotel=hotel)

# Book hotel route
@app.route('/hotels/<int:hotel_id>/book', methods=['GET', 'POST'])
@login_required
def book_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    rooms = Room.query.filter_by(hotel_id=hotel_id).all()

    if request.method == 'POST':
        room_id = request.form['room']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']

        # Create a new booking record
        booking = Booking(user_id=current_user.id, room_id=room_id, check_in_date=check_in_date, check_out_date=check_out_date)
        db.session.add(booking)
        db.session.commit()

        flash('Booking successful!', 'success')
        return redirect(url_for('bookings'))

    return render_template('book_hotel.html', hotel=hotel, rooms=rooms)

# Bookings route (requires login)
@app.route('/bookings')
@login_required
def bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', bookings=bookings)

# Search available rooms route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Retrieve search criteria from the form
        location = request.form['location']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        room_type = request.form['room_type']
        amenities = request.form.getlist('amenities')

        # Perform the search based on the criteria
        query = Hotel.query.filter(Hotel.location.ilike(f"%{location}%"))
        query = query.filter(Hotel.room_type == room_type)

        if check_in_date and check_out_date:
            check_in = time.strptime(check_in_date, "%Y-%m-%d")
            check_out = time.strptime(check_out_date, "%Y-%m-%d")
            query = query.filter(Hotel.rooms.any(Room.id.notin_(get_unavailable_rooms(check_in, check_out))))

        if amenities:
            query = query.filter(Hotel.amenities.any(Amenity.id.in_(amenities)))

        results = query.all()

        return render_template('search_results.html', results=results)

    return render_template('search.html', amenities=Amenity.query.all())

# Helper function to get unavailable rooms for a given date range
def get_unavailable_rooms(check_in, check_out):
    bookings = Booking.query.filter((Booking.check_in_date <= check_out) & (Booking.check_out_date >= check_in)).all()
    return [booking.room_id for booking in bookings]

if __name__ == '__main__':
    app.run(debug=True)
