# models.py (unchanged, since you've already added the image field)
class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer)
    price = db.Column(db.Float)
    mileage = db.Column(db.Integer)
    body_type = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    fuel_efficiency = db.Column(db.Integer)
    transmission = db.Column(db.String(50))
    drivetrain = db.Column(db.String(50))
    exterior_color = db.Column(db.String(50))
    interior_color = db.Column(db.String(50))
    engine = db.Column(db.String(100))
    features = db.Column(db.Text)
    description = db.Column(db.Text)
    image = db.Column(db.String(100))
    status = db.Column(db.String(20))  # New, Used, Certified
    featured = db.Column(db.Boolean, default=False)
    vin = db.Column(db.String(17), unique=True)
    stock_number = db.Column(db.String(20))
    date_added = db.Column(db.DateTime, server_default=db.func.now())
