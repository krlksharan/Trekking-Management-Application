from flask import Flask, request, render_template, redirect, flash, url_for, session
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
    return render_template('login.html')

# ================Login Validation================
@app.route('/login', methods=["GET", "POST"])
def login_validation():
    
    if request.form == "GET":
        return render_template("login.html")
  
    
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")
    user = Users.query.filter_by(username=username).first()
    
    if not user:
        return render_template('login.html', error="User doesn't exist")
    
    if not check_password_hash(user.password,password):
        return render_template('login.html', error="Incorrect password")

    
    #-------------Role-------------
    
    if user.role != role:
        return render_template('login.html', error="Incorrect role selected")

    elif user.role == 'admin':
        return redirect (f'/admin/dashboard/{user.username}')
    elif user.role == "TrekkStaff":
        staff = StaffProfile.query.filter_by(staff_id=user.user_id)
        
        #---------------Staff---------------
        
        if not staff:
            return "Staff profile not found"
        else:
            return render_template(f"/staff/dashboard/{user.username}")
        
        #---------------User---------------
        
    elif user.role == "User(Trekker)":
        return redirect (f'/user/dashboard/{user.id}')
    return render_template('login.html', error="Invalid role")
            
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

    return render_template('register.html', success="Registration Successful")

#================Admin Dashboard================
@app.route("/admin/dashboard/<username>")
def admin_dashboard(username):

    total_treks = Trek.query.count()
    total_users = Users.query.count()
    total_staffs = StaffProfile.query.count()
    total_bookings = Booking.query.count()

    active_bookings = Booking.query.filter_by(status="Booked")
    
    
    bookings_by_trek = db.session.query(
        Trek.trek_name, db.func.count(Booking.booking_id)
    ).outerjoin(Booking, Trek.trek_id == Booking.trek_id).group_by(Trek.trek_name).all()

    trek_labels = [item[0] for item in bookings_by_trek]
    booking_counts = [item[1] for item in bookings_by_trek]


    return render_template(
        'admin_dashboard.html',
        username=username,
        total_treks=total_treks,
        total_users=total_users,
        total_staffs=total_staffs,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        trek_labels=trek_labels,
        booking_count=booking_counts
    )

@app.route("/admin/dashboard/treks")
def view_treks():
    treks = Trek.query.all()  
    
    return render_template('trek.html', treks=treks)

@app.route('/admin/assign-trek/<int:staff_id>/<int:trek_id>')
def assign_trek(staff_id, trek_id):

    staff = StaffProfile.query.get_or_404(staff_id)

    trek = Trek.query.get(
    int(staff.assigned_treks)
)
    
    db.session.commit()

    return redirect(request.referrer)

# Add Trek

@app.route('/admin/trek/add', methods=['GET', 'POST'])
def add_trek():
    if 'user.id' not in session or session.get('role')!= 'admin':
        return redirect(url_for('login_validation'))
    
    if request.method == 'POST':
        trek_name=request.form.get('trek_name'),
        location=request.form.get('location'),
        difficulty=request.form.get('difficulty'),
        available_slots=request.form.get('available_slots'),
        staff_id=request.form.get('staff_id')
        start_date=datetime.striptime(request.form.get('start_date'), '%Y-%m-%d').date(),
        end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    
    if request.method == 'GET':
    
        return render_template('trek_form.html', staffs=approve_staff)       
     
# Edit trek
@app.route('/admin/dashboard/edit/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'GET':
        return render_template(
            'trek_form.html',
            trek=trek
        )

    trek.trek_name = request.form.get('trek_name')
    trek.location = request.form.get('location')
    trek.difficulty = request.form.get('difficulty')
    trek.available_slots = request.form.get('available_slots')

    trek.start_date = datetime.strptime(
        request.form.get('start_date'),
        '%Y-%m-%d'
    ).date()

    trek.end_date = datetime.strptime(
        request.form.get('end_date'),
        '%Y-%m-%d'
    ).date()

    db.session.commit()

    return redirect(url_for('view_treks'))
# Delete Trek

@app.route('/admin/dashboard/delete/<int:trek_id>')
def delete_trek(trek_id):
    
    trek = Trek.query.get_or_404(trek_id)
    
    db.session.delete(trek)
    db.session.commit()
    
    return redirect('/admin/dashboard/treks')

# Approve Trek
@app.route('/admin/dashboard/approve/<int:trek_id>')
def approve_trek(trek_id):
    
    trek = Trek.query.get_or_404(trek_id)
    
    trek.status = 'Approved'
    db.session.commit()
    
    return redirect(url_for("view_treks"))

# Approve Staff

@app.route('/admin/staff/approve/<int:staff_id>')
def approve_staff(staff_id):
    
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.approve_status = "Pending"
    db.session.commit()
    
    return redirect(request.refferer)

@app.route('/admin/staff/blacklist/<int:staff_id>')
def blacklist_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    
    staff.is_blacklisted = True
    
    db.session.commit()
    
    
    return redirect('/admin/staffs')

# ================Staff Dashboard================
@app.route("/staff/dashboard/<username>")
def staff_dashboard(username):
    
    user = Users.query.filter_by(username=username).first_or_404()
    staff_data = StaffProfile.query.filter_by(staff_id=user.id).all()
    trek_data = Trek.query.filter_by(staff_id=user.id).all()
    
    return render_template('staff_dashboard.html', username=username, staff_profiles=staff_data, treks=trek_data )


@app.route('/staff/update-trek/<int:trek_id>',
        methods=['POST'])
def update_trek(trek_id):

    if not user:
            return redirect('/login')
    trek = Trek.query.get_or_404(trek_id)

    trek.available_slots = request.form.get(
        'available_slots'
    )

    trek.status = request.form.get(
        'status'
    )

    db.session.commit()

    return redirect(request.referrer)

@app.route('/staff/trek/<int:trek_id>/users')
def trek_users(trek_id):

    bookings = Booking.query.filter_by(
        trek_id=trek_id
    ).all()

    return render_template(
        'trek_users.html',
        bookings=bookings   
    )
    
# Update slot

@app.route('/staff/update_slots/<int:trek_id>',
           methods=['POST'])
def update_slots(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    trek.available_slots = request.form.get(
        'available_slots'
    )

    db.session.commit()

    return redirect(request.referrer)
# ================User Trekker================
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