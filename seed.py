from app import *
from werkzeug.security import generate_password_hash
from models import Users, Trek, StaffProfile, Booking


def seed_database():
    print("⏳Opening Database session workspace....")
    
    with app.app_context():
        
        
        db. drop_all()
        print("--------------------Droping Database-------------------")
        
        
        db.create_all()
        print("-------------------Creating Database-------------------")
        
                   
            
            #================Super User================
            
        admin = Users(
            username= "lokesh@study.iitm.ac.in",
            password= generate_password_hash('admin@123'),
            role= "admin"
        )
        admin2 = Users(
            username= "admin",
            password= generate_password_hash('admin@123'),
            role= "admin"
        )
        print("User already exists")
        
        trekker = Users(
        username="lokesh",
        password=generate_password_hash("user123"),
        role="User(Trekker)"
        )
    
            #================Verified Crew================
            
        staff = Users(
            username="staff1",
            password=generate_password_hash("staff123"),
            role="Trekk Staff"
        )
        
        db.session.add(staff)
        db.session.commit()
        
               
        # Approve staff
        staff_profile = StaffProfile(
            staff_id = staff.id,
            approval_status="Approved",
            status = "Active"
        )
        
        db.session.add(staff_profile)
        
        # Sample Trails
        trek1 = Trek(
            trek_name="Roopkund Pass",
            location="Uttarakhand",
            difficulty="Hard",
            available_slots=20,
            status="Open"
        )

        trek2 = Trek(
            trek_name="Valley of Flowers",
            location="Uttarakhand",
            difficulty="Moderate",
            available_slots=15,
            status="Pending"
        )
        
        
        db.session.add_all([admin, admin2, staff])
        db.session.commit()
        
        
        db.session.add_all([trek1, trek2])
        db.session.commit()
            
        print("🌟 Success: Database seeding pipeline run completed perfectly!")
            
if __name__ == "__main__":
    seed_database()
            
            
            