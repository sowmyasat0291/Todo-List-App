from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Role definitions
ROLES = {
    'admin': 'admin',
    'manager': 'manager',
    'team_lead': 'team_lead',
    'user': 'user',
}

# Role-based access control
def role_required(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                flash('You must be logged in to access this page.')
                return redirect(url_for('login'))
            username = session['username']
            user = User.query.filter_by(username=username).first()
            if not user or user.role != required_role:
                flash('You do not have permission to access this page.')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

@app.context_processor
def inject_roles():
    return dict(roles=ROLES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')  # Default to 'user' if no role is provided
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
        elif role not in ROLES.values():
            flash('Invalid role selected.')
        else:
            new_user = User(username=username, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html', roles=ROLES)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_tasks = Task.query.filter_by(owner=user).all()
    return render_template('index.html', tasks=user_tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        task_content = request.form['task']
        username = session['username']
        user = User.query.filter_by(username=username).first()
        new_task = Task(content=task_content, owner=user)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:task_id>')
def delete(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter_by(username=username).first()
    task = Task.query.filter_by(id=task_id, owner=user).first()
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/manage')
@role_required('manager')
def manage():
    all_tasks = Task.query.join(User).filter(User.role == 'user').all()
    grouped_tasks = {}
    for task in all_tasks:
        if task.owner.username not in grouped_tasks:
            grouped_tasks[task.owner.username] = []
        grouped_tasks[task.owner.username].append(task)
    return render_template('manage.html', all_tasks=grouped_tasks)

@app.route('/admin')
@role_required('admin')
def admin():
    users_list = User.query.all()
    return render_template('admin.html', users=users_list, roles=ROLES)

# Manually set an initial admin user
if not User.query.filter_by(username='admin').first():
    admin_user = User(username='admin', password='admin_password', role='admin')
    db.session.add(admin_user)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
