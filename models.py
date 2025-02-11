from sqlalchemy import Column, String, Integer, Float, Text, MetaData
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# MetaData configuration for naming conventions (e.g., foreign keys)
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy
db = SQLAlchemy(metadata=metadata)


class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admins'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)  # Unique name
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)

    serialize_rules = ('-password_hash',) 

    def set_password(self, password):
       self.password_hash = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin(id={self.id}, name={self.name}, email={self.email})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'  # Explicit table name for clarity

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)  # Unique name
    category_name = db.Column(String(100), nullable=False)
    subcategory_name = db.Column(String(100), nullable=False)
    description = db.Column(Text, nullable=False)
    price = db.Column(Float, nullable=False)
    image_url = db.Column(String(1000), nullable=True)
    clicks = db.Column(Integer, default=0)

    serialize_rules = ('-clicks',)  # Exclude clicks from serialization

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, category={self.category_name}, price={self.price})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_name": self.category_name,
            "subcategory_name": self.subcategory_name,
            "price": self.price,
            "image_url": self.image_url,
            "clicks": self.clicks
        }


class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)  # Unique name
    description = db.Column(String(500), nullable=True)
    price = db.Column(Float, nullable=False)
    category_name = db.Column(String(100), nullable=False)
    subcategory_name = db.Column(String(100), nullable=False)
    before_service_image = db.Column(String(1000), nullable=True)  # New field for before service image
    after_service_image = db.Column(String(1000), nullable=True)   # New field for after service image
    clicks = db.Column(Integer, default=0)

    serialize_rules = ('-clicks',)  # Exclude clicks from serialization

    def __repr__(self):
        return f"<Service(id={self.id}, name={self.name}, price={self.price}, category={self.category_name})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_name': self.category_name,
            'subcategory_name': self.subcategory_name,
            'before_service_image': self.before_service_image,  # Updated key
            'after_service_image': self.after_service_image,    # Updated key
            'clicks': self.clicks,
        }
   

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)  # Foreign key for product (nullable)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)  # Foreign key for service (nullable)
    name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.Column(db.String(25), nullable=True)
    status=db.Column(db.String(255), nullable=True)
    amount_paid=db.Column(db.String(255), nullable=True)

    # Relationships
    product = db.relationship('Product', backref=db.backref('bookings', lazy=True))
    service = db.relationship('Service', backref=db.backref('bookings', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'service_id': self.service_id,
            'name': self.name,
            'phone': self.phone,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'appointment': self.appointment,
            'status': self.status, 
            'amount_paid': self.amount_paid,
        }

    def __repr__(self):
        return f'<Booking(id={self.id}, product_id={self.product_id}, service_id={self.service_id}, name={self.name}, phone={self.phone}, message={self.message}, timestamp={self.timestamp} , appointment={self.appointment} , status={self.status}, amount_paid={self.amount_paid} )>'
    
    