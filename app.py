from flask import Flask, request, render_template, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from models import db, Users, Trek, StaffProfile, UserProfile, Booking
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io # memory space in the server for storing the plot image
import base64 # Encode the plot image in base64 to embed it in HTML


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login_validation'))

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

    if selected_role == 'TrekkStaff':
        if StaffProfile.query.filter_by(name=name).first():
            return render_template('register.html', error="Staff name already exists")

    new_account = Users(
        username=username,
        password=hashed_pass,
        role=selected_role
    )
   
    try:
        db.session.add(new_account)
        db.session.flush()
        
        if selected_role == 'TrekkStaff':
            new_staff = StaffProfile(
                staff_id=new_account.id,
                name=name,
                contact_details=contact_details
            )
            db.session.add(new_staff)
        elif selected_role == 'User(Trekker)':
            new_user = UserProfile(
                user_id=new_account.id,
                name=name,
                contact_details=contact_details
            )
            db.session.add(new_user)

        db.session.commit()
        return render_template('register.html', success="Registration Successful")
    except Exception as e:
        db.session.rollback()
        return render_template('register.html', error="Registration failed. Please check your details or try a different name.")

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

    # Matplotlib graph
    plt.figure(figsize=(8, 5))
    plt.bar(trek_labels, booking_counts, color='#4CAF50')
    plt.xlabel('Trek Name')
    plt.ylabel('Number of Registered Users')
    plt.title('Users Registered per Trek')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    
    # Encode the image in base64 to embed it in HTML
    plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    plot_url = f"data:image/png;base64,{plot_data}"

    return render_template(
        'admin_dashboard.html',
        username=username,
        total_treks=total_treks,
        total_users=total_users,
        total_staffs=total_staffs,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        plot_url=plot_url
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

    return redirect(request.referrer or url_for('manage_treks'))

# Add Trek

@app.route('/admin/trek/add', methods=['GET', 'POST'])
def add_trek():
    if request.method == 'POST':
        trek_name = request.form.get('trek_name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        available_slots = request.form.get('available_slots')
        staff_id = request.form.get('staff_id')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        new_trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            staff_id=staff_id if staff_id else None,
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('manage_treks'))
    
    if request.method == 'GET':
        staffs = StaffProfile.query.filter_by(approval_status='Approved').all()
        return render_template('trek_form.html', staffs=staffs)       
     
# Edit trek
@app.route('/admin/dashboard/edit/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'GET':
        staffs = StaffProfile.query.filter_by(approval_status='Approved').all()
        return render_template(
            'trek_form.html',
            trek=trek,
            staffs=staffs
        )

    trek.trek_name = request.form.get('trek_name')
    trek.location = request.form.get('location')
    trek.difficulty = request.form.get('difficulty')
    trek.duration = request.form.get('duration')
    trek.available_slots = request.form.get('available_slots')
    
    staff_id = request.form.get('staff_id')
    trek.staff_id = staff_id if staff_id else None

    trek.start_date = datetime.strptime(
        request.form.get('start_date'),
        '%Y-%m-%d'
    ).date()

    trek.end_date = datetime.strptime(
        request.form.get('end_date'),
        '%Y-%m-%d'
    ).date()

    db.session.commit()

    return redirect(url_for('manage_treks'))
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
    
    return redirect(url_for("manage_treks"))

# Approve Staff

@app.route('/admin/staff/approve/<int:staff_id>')
def approve_staff(staff_id):
    
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.approval_status = "Approved"
    db.session.commit()
    
    return redirect(request.referrer or '/admin/dashboard/treks')

@app.route('/admin/staffs')
def manage_staffs():
    search_query = request.args.get('search', '')
    if search_query:
        staffs = StaffProfile.query.filter(StaffProfile.name.ilike(f'%{search_query}%') | (StaffProfile.staff_id == search_query if search_query.isdigit() else False)).all()
    else:
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
    search_query = request.args.get('search', '')
    if search_query:
        users = UserProfile.query.filter(UserProfile.name.ilike(f'%{search_query}%') | (UserProfile.user_id == search_query if search_query.isdigit() else False)).all()
    else:
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

@app.route('/admin/bookings')
def admin_bookings():
    bookings = db.session.query(
        Booking.booking_id,
        Booking.user_id,
        UserProfile.name.label('user_name'),
        Trek.trek_name,
        Booking.booking_date,
        Booking.status
    ).join(UserProfile, Booking.user_id == UserProfile.user_id)\
     .join(Trek, Booking.trek_id == Trek.trek_id).all()
    return render_template('admin_bookings.html', bookings=bookings)

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
    staff_id = request.form.get('staff_id')
    
    if str(trek.staff_id) != str(staff_id):
        return "Unauthorized: You are not assigned to this trek", 403

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
    query = Trek.query.filter(Trek.status.in_(['Approved', 'Open']))
    
    search_term = request.args.get('search')
    difficulty = request.args.get('difficulty')
    location = request.args.get('location')

    if search_term:
        query = query.filter(Trek.trek_name.ilike(f"%{search_term}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
        
    treks = query.all()
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

@app.route('/user/booking/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    user_id = booking.user_id
    if booking.status == 'Booked':
        booking.status = 'Cancelled'
        trek = Trek.query.get(booking.trek_id)
        if trek:
            trek.available_slots += 1
        db.session.commit()
    return redirect(url_for('user_dashboard', user_id=user_id))

@app.route('/user/profile/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    user_prof = UserProfile.query.get_or_404(user_id)
    if request.method == 'POST':
        user_prof.name = request.form.get('name')
        user_prof.contact_details = request.form.get('contact_details')
        db.session.commit()
        return redirect(url_for('user_dashboard', user_id=user_id))
    return render_template('edit_user_profile.html', user_prof=user_prof)

    
if __name__ == "__main__":
    
    app.run(host='localhost', port=5000, debug=True)