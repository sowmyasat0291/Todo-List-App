from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# In-memory storage for users, roles, and tasks
users = {}
roles = {}
tasks = {}

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
            user_role = roles.get(username)
            if user_role != required_role:
                flash('You do not have permission to access this page.')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

@app.context_processor
def inject_roles():
    return dict(roles=roles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
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
        
        if username in users:
            flash('Username already exists. Please choose a different one.')
        elif role not in ROLES.values():
            flash('Invalid role selected.')
        else:
            users[username] = password
            roles[username] = role
            tasks[username] = []  # Initialize an empty task list for the new user
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
    user_tasks = tasks.get(username, [])
    return render_template('index.html', tasks=user_tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        task_content = request.form['task']
        username = session['username']
        tasks[username].append(task_content)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:task_id>')
def delete(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user_tasks = tasks.get(username, [])
    if 0 <= task_id < len(user_tasks):
        del user_tasks[task_id]
    return redirect(url_for('index'))

@app.route('/manage')
@role_required('manager')
def manage():
    all_tasks = {user: task_list for user, task_list in tasks.items() if roles.get(user) == 'user'}
    return render_template('manage.html', all_tasks=all_tasks)

@app.route('/admin')
@role_required('admin')
def admin():
    return render_template('admin.html', users=users, roles=roles)
# Manually set an initial admin user
users['admin'] = 'admin_password'
roles['admin'] = 'admin'
tasks['admin'] = []

if __name__ == '__main__':
    app.run(debug=True)
