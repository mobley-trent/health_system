# Health System Management App

This is a Flask-based web application for managing health programs, clients, and user accounts. The app allows users to create and manage health programs, register clients, enroll clients in programs, and view detailed profiles for both clients and programs.

The live version of the project can be accessed at this [link](https://health-system-sigma.vercel.app/). However, Vercel does not persist the SQLite DB after the session and it will create a new DB for every session.

## Features

- **User Authentication**: Users can register, log in, and manage their accounts.
- **Health Programs**: Create, view, and delete health programs.
- **Client Management**: Register clients, edit their profiles, and delete them.
- **Enrollment**: Enroll clients in health programs and manage their enrollments.
- **Dashboard**: View a list of all health programs and navigate to other features.
- **REST API**: Provides endpoints to fetch client and program data in JSON format.

## Project Structure
```
health_system/
│
├── app/
│   ├── __init__.py          # App factory
│   ├── .env                 # Environment variables
│   ├── routes.py            # Web routes (views)
│   ├── models.py            # Database models
│   ├── templates/           # HTML templates
│   └── static/              # CSS templates
│
├── instance/
│   └── health.db            # SQLite database file
├── run.py                   # Entry point to run the app
├── requirements.txt         # Dependencies
└── README.md
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mobley-trent/health_system.git
    cd health_system
    ```
2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up the environment variables:
    - Create a `.env` file in the `app/` directory and add the following:
      ```
      SECRET_KEY=your_secret_key
      DATABASE_URL=sqlite:///../instance/health.db
      ```
5. Run the application:
    ```bash
    python run.py
    ```
6. Open your browser and go to `http://localhost:5000` to access the app.

## Demonstration

https://github.com/user-attachments/assets/51bdc2df-bc4b-4cb3-9186-4662fcf4a0b2

## Slides

[HEALTH INFORMATION SYSTEM.pptx](https://github.com/user-attachments/files/19928696/HEALTH.INFORMATION.SYSTEM.pptx)


## Page routes
- `/` - Home page (dashboard). Redirects to `/login` if not authenticated
- `/register` - User registration page
- `/login` - User login page
- `/profile` - User profile page
- `/program/<int:program_id>` - View program details
- `/client/register` - Register a new client
- `/client/<int:client_id>` - View client details
- `/client/<int:client_id>/edit` - Edit client profile
- `/clients` - List all clients
- `/client/<int:client_id>/enroll` - Enroll or unenroll client in a program

## API Endpoints
- `/api/clients` - GET: List all clients
- `/api/clients/<int:client_id>` - GET: Get client details

## Acknowledgements
- Flask documentation: https://flask.palletsprojects.com/
- Flask-SQLAlchemy documentation: https://flask-sqlalchemy.palletsprojects.com/
- Flask-Login documentation: https://flask-login.readthedocs.io/
