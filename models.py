from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(
        db.Integer, 
        primary_key = True)
    username = db.Column(
        db.String(50), 
        unique=True, 
        nullable=False)
    password = db.Column(
        db.String(255), 
        nullable=False)
    role = db.Column(
        db.String(20), 
        nullable=False)
    
    
# ===========User Trekker===========
class Trek(db.Model):
    __tablename__ = 'treks'

    trek_id = db.Column(
        db.Integer,
        primary_key=True
    )

    trek_name = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default='Pending'
    )

    start_date = db.Column(
        db.Date
    )

    end_date = db.Column(
        db.Date
    )
    is_blacklisted = db.Column(
        db.Boolean,
        default=False
    )
    
    staff_id = db.Column(
        db.Integer,
        db.ForeignKey('staff_profile.staff_id'),
        nullable=True
    )

class StaffProfile(db.Model):
    __tablename__ = 'staff_profile'

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
        nullable=False
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    contact_details = db.Column(
        db.String(15),
        nullable=False
    )

    assigned_treks = db.Column(
        db.String(200),
        nullable=True
    )
    
    approval_status = db.Column(
        db.String(20),
        default='Pending'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
        nullable=False
    )
    
    name = db.Column(db.String(50), nullable=False)
    contact_details = db.Column(db.String(15), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey('treks.trek_id'),
        nullable=False
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.now
    )

    status = db.Column(
        db.String(20),
        default='Booked'
    )
    
    