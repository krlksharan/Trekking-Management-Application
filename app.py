from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import db, Users, Trek, StaffProfile, Booking


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

     
@app.route('/')
def home():
    return render_template('home.html')

# ================Login Validation================
@app.route('/login', methods=["GET", "POST"])
def login_validation():
    
    if request.method == 'GET':
        return render_template('home.html')
    
    username = request.form.get("username")
    password = request.form.get("password")
    selected_role = request.form.get("role")
    user = Users.query.filter_by(username=username).first()
    
    # print(selected_role, user.role)
    
    if not user:
        return "User doesn't exist"
    
    if not check_password_hash(user.password, password):
        return "Incorrect password"

    if user.role != selected_role:
        return "Incorrect role selected"

    if user.role == "admin":
        return redirect("/admin/dashboard/{user.id}")

    elif user.role == "Trek Staff":
        return redirect(f"/staff/dashboard/{user.id}")

    elif user.role == "User(Trekker)":
        return redirect(f"/user/dashboard/{user.id}")

    return "Invalid role"

@app.route('/register', methods=['GET','POST'])
def registration():
    
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    selected_role = request.form.get('role')

    hashed_pass = generate_password_hash(password)

    exists = Users.query.filter_by(
        username=username
    ).first()

    if exists:
        return "Username already exists"

    new_account = Users(
        username=username,
        password=hashed_pass,
        role=selected_role
    )

    db.session.add(new_account)
    db.session.commit()

    return "Registration successful"

#================Admin Dashboard================
@app.route("/admin/dashboard/<username>")
def admin_dashboard(username):
    active_bookings = Booking.query.all()

    return render_template('admin_dashboard.html', active_bookings=active_bookings,username=username)

# ================Staff Dashboard================
@app.route("/staff/dashboard/<username>")
def staff_dashboard(username):
    return render_template('staff_dashboard.html', username=username)

# ================User Dashboard================
@app.route("/user/dashboard/<user_id>")
def user_dashboard(user_id):
    trek = Trek.query.all()
    booking = Booking.query.filter_by(user_id = user_id)
    user = Users.query.filter_by(id= user_id).first()
    return render_template(
        "user_dashboard.html",
        treks=trek,
        bookings=booking,
        user_id=user_id
    )
    

    
if __name__ == "__main__":
    
    app.run(host='localhost', port=5000, debug=True)