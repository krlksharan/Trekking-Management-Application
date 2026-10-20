# 🏔️ Trekking Management Application (TMA)

A web application designed for adventure organizations to streamline trek planning, bookings, staff coordination, and participant management. It replaces manual processes and spreadsheets with automated capacity tracking, role-based dashboards, and structured approvals.

---

## 📌 Features

- **Role-Based Dashboards**: Tailored views and controls for Trek Organizers, Staff members, and Participants.
- **Trek Management & Approvals**: Create, update, review, and approve planned treks and expeditions.
- **Automated Capacity & Booking Control**: Real-time slot management to prevent overbooking.
- **Trek History & Logs**: Centralized records of completed treks, participants, and staff assignments.
- **RESTful API Documentation**: OpenAPI/Swagger specification (`api.yaml`) included for API integration.
- **Responsive UI**: Clean, mobile-friendly interface built with Bootstrap.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite / SQLAlchemy ORM
- **Frontend**: HTML5, Jinja2 Templates, Bootstrap CSS
- **API Spec**: OpenAPI 3.0 (`api.yaml`)

---

## 📂 Project Structure

```text
├── instance/               # SQLite database instance
├── templates/              # Jinja2 HTML templates
├── .venv/                  # Virtual environment (local)
├── api.yaml                # OpenAPI / Swagger specification
├── app.py                  # Main Flask application and route definitions
├── models.py               # Database models and schemas
├── requirements.txt        # Python package dependencies
├── seed.py                 # Seed script for initial test data
└── README.md               # Project documentation
