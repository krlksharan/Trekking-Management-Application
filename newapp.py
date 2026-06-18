from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template('home.html')

# ================Login Validation================
@app.route('/login_validation', method=["POST"])
def login_validation():
    username = request.form.get("username")
    password = request.form.get("password")
    hashed_password = generate_password_hash(password)
    selected_role = request.form.get("user_role")

    exists  = User.query.filter_by(username = username).first()
    if not exist:
        
        

#================Admin Dashboard================


active_bookings = [
    {
        "name": "Himalayan Trek",
        "location": "Manali",
        "assigned_staff_id": 201,
        "status": "Active"
    },
    {
        "name": "Valley Trek",
        "location": "Kashmir",
        "assigned_staff_id": 202,
        "status": "Active"
    },
    {
        "name": "Forest Adventure",
        "location": "Coorg",
        "assigned_staff_id": 203,
        "status": "In Progress"
    }
]

@app.route("/admin/dashboard")
def admin_dasbhoard():
    return render_template('admin_dashboard.html', active_bookings=active_bookings )

# ================Staff Dashboard================
@app.route("/staff/dashboard/<username>")
def staff_dashboard(username):
    return render_template('staff_dashboard.html', username=username)

# ================User Dashboard================
treks = [
        {
            "trek_id": 1,
            "trek_name": "Himalayan Trek",
            "trek_location": "Manali",
            "start_date": "2026-07-01"
        },
        {
            "trek_id": 2,
            "trek_name": "Valley Trek",
            "trek_location": "Kashmir",
            "start_date": "2026-07-10"
        }
    ]

bookings = [
    {
        "booking_id": 101,
        "trek_name": "Himalayan Trek",
        "status": "Booked"
    },
    {
        "booking_id": 102,
        "trek_name": "Valley Trek",
        "status": "Cancelled"
    }
]


@app.route("/user/dashboard/<username>")
def user_dashboard(username):

    return render_template(
        "user_dashboard.html",
        treks=treks,
        bookings=bookings,
        username=username
    )
    

    
if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)