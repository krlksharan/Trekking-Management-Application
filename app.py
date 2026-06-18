from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"

db = SQLAlchemy(app)

class admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)
    role = db.Column(db.String(12), nullable=False)
    
class trekk_staff(db.Model):
    __tablename__ = 'trekk_staff'

class user_trakker(db.Model):
    __tablename__ = 'user_trakker'


@app.route("/")
def home():
   return render_template('home.html')

# =================Admin==================
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html", ) 
    
# =================Add Trek==================
@app.route("/admin/add", methods = ['POST'])
def admin_add():
    trek_id = request.form.get("trek_id")
    trek_name = request.form.get("trek_name")
    location = request.form.get("location")
    duration = request.form.get("duration")
    slots = request.form.get("slots")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    
    return "<h2>Trek Added Successfully</h2>"
    
# =================Edit Trek==================  
@app.route("/admin/edit/<int:trek_id>", methods=['POST'])
def admin_edit(trek_id):
    
    trek = Trek.get(trek_id)
    trek.trek_id = request.form.get("trek_id")
    trek_name = request.form.get("trek_name")
    location = request.form.get("location")
    duration = request.form.get("duration")
    slots = request.form.get("slots")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    db.commit()
    return "<h2>Trek Updated Successfully</h2>"

# =================Form Submit=================
@app.route('/login-validation', methods=['POST'])
def login_submit():
    username = request.form.get('username')
    password = request.form.get('password')
    selected_role = request.form.get('user_role')
    if not username or not password:
        return redirect('/')
    
    if selected_role == 'admin':
        return redirect('/admin/dashboard')
    
    elif selected_role == 'staff':
        staff_login = username.lower().replace(" ", "-")
        return redirect(f'/staff/dashboard/{staff_login}')
    
    elif selected_role == 'user':
        user_login = username.lower().replace(" ", "-")
        return redirect(f'/user/dashboard/{user_login}')
    
    return redirect('/')
    
# =================Staff Login==================
@app.route('/staff/dashboard/<staff>')
def staff_login(staff):
    return render_template("staff_dashboard.html", staff_name=staff.replace("-", " ").title())

@app.route('/user/dashboard/<username>')
def trekker(username):
    profile = {
        "name": username.replace("-", " ").title()
    }
    return render_template("user_dashboard.html", username=username, profile=profile)


    
if __name__ == "__main__":
    app.run(host='localhost', port=8000, debug=True)