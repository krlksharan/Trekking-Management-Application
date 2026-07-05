from app import *
from werkzeug.security import generate_password_hash
from models import Users, Trek, StaffProfile, Booking


def seed_database():
    print("⏳Opening Database session workspace....")
    
    with app.app_context():
        
        db.drop_all()
        print("--------------------Droping Database-------------------")
        
        db.create_all()
        print("-------------------Creating Database-------------------")
        
        #================Super User================
        
        admin = Users(
            username="lokesh@study.iitm.ac.in",
            password=generate_password_hash('admin@123'),
            role="admin"
        )
        
        admin2 = Users(
            username="admin",
            password=generate_password_hash('admin@123'),
            role="admin"
        )
        
        db.session.add_all([admin, admin2])
        db.session.commit()
        
        print("🌟 Success: Database seeding pipeline run completed perfectly!")
            
if __name__ == "__main__":
    seed_database()