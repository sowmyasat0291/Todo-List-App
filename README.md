Step-by-Step Explanation
Importing Modules:

Flask, render_template, request, redirect, url_for, flash, and session are imported from Flask for web app functionality.
SQLAlchemy is used for database operations.
IntegrityError handles database integrity issues.
Initialize Flask and SQLAlchemy:

app = Flask(__name__) initializes the Flask application.
app.config['SECRET_KEY'] sets a secret key for session management.
app.config['SQLALCHEMY_DATABASE_URI'] configures the SQLite database URI.
db = SQLAlchemy(app) initializes SQLAlchemy with the Flask app.
Define Models:

User and Task classes define database models for users and tasks, respectively.
User has a relationship with Task (one-to-many).
Role Definitions:

A dictionary ROLES is defined to manage different user roles.
Role-Based Access Control:

role_required(required_role) is a decorator that restricts access based on user roles.
Context Processor:

inject_roles() makes the ROLES dictionary available in templates.
Routes:

/login: Handles user login.
/register: Handles user registration.
/logout: Logs the user out.
/: Displays the logged-in user’s tasks.
/add: Allows adding new tasks.
/delete/<int:task_id>: Deletes a specific task.
/manage: Manages tasks for managers.
/admin: Admin panel for admin users.
Initial Setup:

Checks if an initial admin user exists and creates one if not.
Running the App:

app.run(debug=True) starts the Flask development server with debug mode enabled.
