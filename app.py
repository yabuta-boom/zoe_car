import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime
from some_module import CodeReference

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# App Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zoe_dealership.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yeabseramekbeb@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'yeabseramekbeb@gmail.com'
app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
csrf = CSRFProtect(app)

# Models
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    body_type = db.Column(db.String(30))
    featured = db.Column(db.Boolean, default=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    interest = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def verify_recaptcha(response):
    secret = app.config['RECAPTCHA_SECRET_KEY']
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={'secret': secret, 'response': response})
    return r.json().get('success', False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def home():
    featured = Vehicle.query.filter_by(featured=True).limit(6).all()
    return render_template('index.html', featured_vehicles=featured)

@app.route('/inventory')
def inventory():
    make = request.args.get('make')
    model = request.args.get('model')
    min_year = request.args.get('min_year')
    max_price = request.args.get('max_price')
    body_type = request.args.get('body_type')

    query = Vehicle.query
    if make:
        query = query.filter_by(make=make)
    if model:
        query = query.filter_by(model=model)
    if min_year:
        query = query.filter(Vehicle.year >= int(min_year))
    if max_price:
        query = query.filter(Vehicle.price <= float(max_price))
    if body_type:
        query = query.filter_by(body_type=body_type)

    vehicles = query.all()
    makes = db.session.query(Vehicle.make).distinct().all()
    models = db.session.query(Vehicle.model).distinct().all()
    body_types = db.session.query(Vehicle.body_type).distinct().all()

    return render_template('inventory.html',
                           vehicles=vehicles,
                           makes=[m[0] for m in makes],
                           models=[m[0] for m in models],
                           body_types=[b[0] for b in body_types],
                           filters=request.args)

@app.route('/vehicle/<int:vehicle_id>')
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    image_url = url_for('static', filename='uploads/' + vehicle.image) if vehicle.image else None
    return render_template('details.html', vehicle=vehicle, image_url=image_url)

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        price = float(request.form['price'])
        body_type = request.form['body_type']
        featured = 'featured' in request.form

        image_file = request.files.get('file')
        filename = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_vehicle = Vehicle(
            make=make,
            model=model,
            year=year,
            price=price,
            body_type=body_type,
            image=filename,
            featured=featured
        )
        try:
            db.session.add(new_vehicle)
            db.session.commit()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding vehicle: {str(e)}', 'danger')

    return render_template('add_vehicle.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    recaptcha_error = False
    
    if form.validate_on_submit():
        if not verify_recaptcha(request.form.get('g-recaptcha-response')):
            recaptcha_error = True
            flash('Please complete the CAPTCHA verification', 'danger')
        else:
            try:
                new_contact = ContactRequest(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    message=form.message.data,
                    interest=form.interest.data
                )
                db.session.add(new_contact)
                db.session.commit()

                msg = Message(
                    subject=f"New Contact: {form.interest.data}",
                    recipients=["yeabseramekbeb@gmail.com"],
                    body=f"""Name: {form.name.data}
Email: {form.email.data}
Phone: {form.phone.data}
Interest: {form.interest.data}
Message: {form.message.data}"""
                )
                mail.send(msg)
                
                flash('Message sent successfully!', 'success')
                return redirect(url_for('contact'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
    
    return render_template('contact.html',
                         form=form,
                         recaptcha_site_key=app.config['RECAPTCHA_SITE_KEY'],
                         recaptcha_error=recaptcha_error)
@app.route('/test-recaptcha')
def test_recaptcha():
    return f"""
    reCAPTCHA Site Key: {app.config['RECAPTCHA_SITE_KEY']}<br>
    reCAPTCHA Secret Key: {app.config['RECAPTCHA_SECRET_KEY'][:3]}... (hidden for security)
    """
# Error Handling
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# Run the App
if __name__ == '__main__':
    app.run(debug=True)
