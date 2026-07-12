from flask import Flask, request, render_template, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import db, Users, Trek, StaffProfile, UserProfile, Booking


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
    
    if request.method == "GET":
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

    if user.role == 'admin':
        return redirect (f'/admin/dashboard/{user.username}')
    elif user.role == "TrekkStaff":
        staff = StaffProfile.query.filter_by(staff_id=user.id).first()
        
        #---------------Staff---------------
        
        if not staff:
            return render_template('login.html', error="Staff profile not found")
        elif staff.is_blacklisted:
            return render_template('login.html', error="Your account has been blacklisted")
        elif staff.approval_status != 'Approved':
            return render_template('login.html', error="Your account is pending admin approval")
        else:
            return redirect(f"/staff/dashboard/{user.username}")
        
        #---------------User---------------
        
    elif user.role == "User(Trekker)":
        user_prof = UserProfile.query.filter_by(user_id=user.id).first()
        if user_prof and user_prof.is_blacklisted:
            return render_template('login.html', error="Your account has been blacklisted")
        return redirect (f'/user/dashboard/{user.id}')
    return render_template('login.html', error="Invalid role")
            
@app.route('/register', methods=['GET','POST'])
def registration():
    
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    selected_role = request.form.get('role')
    name = request.form.get('name')
    contact_details = request.form.get('contact_details')

    hashed_pass = generate_password_hash(password)

    exists = Users.query.filter_by(
        username=username
    ).first()

    if exists:
        return render_template('register.html', error="Username already exists")

    new_account = Users(
        username=username,
        password=hashed_pass,
        role=selected_role
    )
   
    db.session.add(new_account)
    db.session.commit()
    
    if selected_role == 'TrekkStaff':
        new_staff = StaffProfile(
            staff_id=new_account.id,
            name=name,
            contact_details=contact_details
        )
        db.session.add(new_staff)
        db.session.commit()
    elif selected_role == 'User(Trekker)':
        new_user = UserProfile(
            user_id=new_account.id,
            name=name,
            contact_details=contact_details
        )
        db.session.add(new_user)
        db.session.commit()

    return render_template('register.html', success="Registration Successful")

#================Admin Dashboard================
@app.route("/admin/dashboard/<username>")
def admin_dashboard(username):

    total_treks = Trek.query.count()
    total_users = UserProfile.query.count()
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
def manage_treks():
    search_query = request.args.get('search', '')

    if search_query:
        treks = Trek.query.filter(Trek.trek_name.ilike(f'%{search_query}%')).all()
    else:
        treks = Trek.query.all()
    return render_template('manage_treks.html', treks=treks)

@app.route('/admin/assign-trek/<int:staff_id>/<int:trek_id>')
def assign_trek(staff_id, trek_id):

    staff = StaffProfile.query.get_or_404(staff_id)
    trek = Trek.query.get_or_404(trek_id)

    trek.staff_id = staff.staff_id
    
    db.session.commit()

    return redirect(request.referrer or url_for('view_treks'))

# Add Trek

@app.route('/admin/trek/add', methods=['GET', 'POST'])
def add_trek():
    if request.method == 'POST':
        trek_name = request.form.get('trek_name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        available_slots = request.form.get('available_slots')
        staff_id = request.form.get('staff_id')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        new_trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            available_slots=available_slots,
            staff_id=staff_id if staff_id else None,
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('view_treks'))
    
    if request.method == 'GET':
        staffs = StaffProfile.query.filter_by(approval_status='Approved').all()
        return render_template('trek_form.html', staffs=staffs)       
     
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
    staff.approval_status = "Approved"
    db.session.commit()
    
    return redirect(request.referrer or '/admin/dashboard/treks')

@app.route('/admin/staffs')
def manage_staffs():
    staffs = StaffProfile.query.all()
    return render_template('manage_staffs.html', staffs=staffs)

@app.route('/admin/staff/blacklist/<int:staff_id>')
def blacklist_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    
    staff.is_blacklisted = True
    
    db.session.commit()
    
    return redirect('/admin/staffs')

@app.route('/admin/users')
def manage_users():
    users = UserProfile.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/user/blacklist/<int:user_id>')
def blacklist_user(user_id):
    user_prof = UserProfile.query.get_or_404(user_id)
    user_prof.is_blacklisted = True
    db.session.commit()
    
    return redirect(url_for('manage_users'))

@app.route('/admin/staff/unblacklist/<int:staff_id>')
def unblacklist_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.is_blacklisted = False
    db.session.commit()
    return redirect('/admin/staffs')

@app.route('/admin/user/unblacklist/<int:user_id>')
def unblacklist_user(user_id):
    user_prof = UserProfile.query.get_or_404(user_id)
    user_prof.is_blacklisted = False
    db.session.commit()
    return redirect(url_for('manage_users'))

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

    bookings = db.session.query(
        Booking.booking_id,
        UserProfile.name.label('user_name'),
        UserProfile.contact_details,
        Booking.booking_date,
        Booking.status
    ).join(UserProfile, Booking.user_id == UserProfile.user_id)\
     .filter(Booking.trek_id == trek_id).all()

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
    treks = Trek.query.all()
    bookings = db.session.query(
        Booking.booking_id,
        Trek.trek_name,
        Booking.booking_date,
        Booking.status
    ).join(Trek, Booking.trek_id == Trek.trek_id)\
     .filter(Booking.user_id == user_id).all()
     
    user = Users.query.filter_by(id= user_id).first()
    return render_template(
        "user_dashboard.html",
        treks=treks,
        bookings=bookings,
        user_id=user_id
    )

@app.route('/user/book/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    user_id = request.form.get('user_id')
    trek = Trek.query.get_or_404(trek_id)
    
    if trek.status != 'Open':
        return "Trek is not open for booking", 400
        
    if trek.available_slots <= 0:
        return "No available slots", 400
        
    existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).first()
    if existing_booking:
        return "Already booked", 400
        
    new_booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        status='Booked'
    )
    
    trek.available_slots -= 1
    
    db.session.add(new_booking)
    db.session.commit()
    
    return redirect(url_for('user_dashboard', user_id=user_id))

    
if __name__ == "__main__":
    
    app.run(host='localhost', port=5000, debug=True)