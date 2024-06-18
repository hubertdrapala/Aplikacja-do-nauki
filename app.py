from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    username TEXT UNIQUE,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    description TEXT,
                    due_date TEXT,
                    is_completed BOOLEAN)''')
    c.execute('''CREATE TABLE IF NOT EXISTS finances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    description TEXT,
                    date TEXT,
                    type TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', logged_in=True)
    else:
        return render_template('index.html', logged_in=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/add_task')
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_task.html')

@app.route('/api/add_task', methods=['POST'])
def api_add_task():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    data = request.json
    print('Otrzymane dane:', data) # Dodane logowanie
    
    db = get_db()
    c = db.cursor()
    try:
        c.execute('''INSERT INTO tasks (user_id, title, description, due_date, is_completed)
                     VALUES (?, ?, ?, ?, ?)''', (session['user_id'], data['title'], data['description'], data['due_date'], False))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        print('Błąd podczas dodawania zadania:', e) # Dodane logowanie
        return jsonify({'success': False, 'error': str(e)})

@app.route('/check_finances')
def check_finances():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM finances WHERE user_id=?', (session['user_id'],))
    finances = c.fetchall()
    return render_template('check_finances.html', finances=finances)


@app.route('/api/add_finance', methods=['POST'])
def api_add_finance():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    data = request.json
    db = get_db()
    c = db.cursor()
    try:
        c.execute('''INSERT INTO finances (user_id, amount, description, date, type)
                     VALUES (?, ?, ?, ?, ?)''', (session['user_id'], data['amount'], data['description'], data['date'], data['type']))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/task_info')
def task_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, title, description, due_date, is_completed FROM tasks WHERE user_id=?', (session['user_id'],))
    tasks = c.fetchall()
    
    return render_template('task_info.html', tasks=tasks)

@app.route('/api/task_info', methods=['GET'])
def api_task_info():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, title, description, due_date, is_completed FROM tasks WHERE user_id=?', (session['user_id'],))
    tasks = c.fetchall()
    
    tasks_list = [{'id': task[0], 'title': task[1], 'description': task[2], 'due_date': task[3], 'is_completed': task[4]} for task in tasks]
    return jsonify({'success': True, 'tasks': tasks_list})


@app.route('/task-detail/<int:task_id>')
def task_detail(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM tasks WHERE id=? AND user_id=?', (task_id, session['user_id']))
    task = c.fetchone()
    if not task:
        return 'Task not found', 404
    return render_template('task_detail.html', task=task)

@app.route('/edit_tasks')
def edit_tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, title FROM tasks WHERE user_id=?', (session['user_id'],))
    tasks = c.fetchall()
    return render_template('edit_tasks.html', tasks=tasks)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    c = db.cursor()
    if request.method == 'POST':
        data = request.form
        c.execute('''UPDATE tasks SET title=?, description=?, due_date=?, is_completed=? WHERE id=? AND user_id=?''',
                  (data['title'], data['description'], data['due_date'], 'is_completed' in data, task_id, session['user_id']))
        db.commit()
        return redirect(url_for('edit_tasks'))
    c.execute('SELECT * FROM tasks WHERE id=? AND user_id=?', (task_id, session['user_id']))
    task = c.fetchone()
    if not task:
        return 'Task not found', 404
    return render_template('edit_task.html', task=task)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''INSERT INTO users (email, username, password) VALUES (?, ?, ?)''',
                      (data['email'], data['username'], hashed_password))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 400
        conn.close()
        return jsonify({'success': True}), 200
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=?', (data['username'],))
        user = c.fetchone()
        
        if user and check_password_hash(user[3], data['password']):
            session['user_id'] = user[0]
            session['username'] = user[2]
            conn.close()
            return jsonify({'success': True}), 200
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    return render_template('login.html')




@app.route('/finance_info')
def finance_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM finances WHERE user_id=?', (session['user_id'],))
    finances = c.fetchall()
    
    return render_template('finance_info.html', finances=finances)

@app.route('/api/finance_info', methods=['GET'])
def api_finance_info():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, amount, description, date, type FROM finances WHERE user_id=?', (session['user_id'],))
    finances = c.fetchall()
    
    finances_list = [{'id': finance[0], 'amount': finance[1], 'description': finance[2], 'date': finance[3], 'type': finance[4]} for finance in finances]
    return jsonify({'success': True, 'finances': finances_list})

if __name__ == '__main__':
    app.run(debug=True)