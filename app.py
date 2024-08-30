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
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id INTEGER,
                    question TEXT,
                    correct_answer TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER,
                    answer TEXT,
                    label TEXT)''')
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
    db = get_db()
    c = db.cursor()
    try:
        c.execute('''INSERT INTO tasks (user_id, title, description, due_date, is_completed)
                     VALUES (?, ?, ?, ?, ?)''', (session['user_id'], data['title'], data['description'], data['due_date'], False))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
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

@app.route('/api/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    data = request.json
    db = get_db()
    c = db.cursor()

    try:
        c.execute('''UPDATE tasks 
                     SET title=?, description=?, due_date=?, is_completed=?
                     WHERE id=? AND user_id=?''', 
                   (data['title'], data['description'], data['due_date'], data['is_completed'], task_id, session['user_id']))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    db = get_db()
    c = db.cursor()
    
    try:
        c.execute('''DELETE FROM tasks WHERE id=? AND user_id=?''', (task_id, session['user_id']))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})

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

@app.route('/create_quiz')
def create_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('create_quiz.html')

@app.route('/api/create_quiz', methods=['POST'])
def api_create_quiz():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    data = request.json
    db = get_db()
    c = db.cursor()
    
    try:
        # Dodaj quiz
        c.execute('''INSERT INTO quizzes (user_id, title) VALUES (?, ?)''',
                  (session['user_id'], data['title']))
        quiz_id = c.lastrowid
        
        # Dodaj pytania i odpowiedzi
        for question_data in data['questions']:
            c.execute('''INSERT INTO questions (quiz_id, question, correct_answer) 
                         VALUES (?, ?, ?)''',
                      (quiz_id, question_data['question'], question_data['correct']))
            question_id = c.lastrowid
            
            for label, answer in question_data['answers'].items():
                c.execute('''INSERT INTO answers (question_id, answer, label) 
                             VALUES (?, ?, ?)''',
                          (question_id, answer, label))
        
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/quiz_list')
def quiz_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, title FROM quizzes WHERE user_id = ?', (session['user_id'],))
    quizzes = c.fetchall()
    return render_template('quiz_list.html', quizzes=quizzes)

@app.route('/api/quiz_list', methods=['GET'])
def api_quiz_list():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT id, title FROM quizzes WHERE user_id = ?', (session['user_id'],))
    quizzes = c.fetchall()
    
    return jsonify({'success': True, 'quizzes': [{'id': q[0], 'title': q[1]} for q in quizzes]})

@app.route('/solve_quiz/<int:quiz_id>')
def solve_quiz_page(quiz_id):
    db = get_db()
    c = db.cursor()
    
    # Pobierz quiz
    c.execute('SELECT id, title FROM quizzes WHERE id = ?', (quiz_id,))
    quiz = c.fetchone()
    
    if not quiz:
        return "Quiz not found", 404
    
    # Pobierz pytania
    c.execute('SELECT id, question FROM questions WHERE quiz_id = ?', (quiz_id,))
    questions = c.fetchall()
    
    questions_data = []
    for q in questions:
        qid = q[0]
        c.execute('SELECT label, answer FROM answers WHERE question_id = ?', (qid,))
        answers = c.fetchall()
        answers_dict = {label: answer for label, answer in answers}
        questions_data.append({'id': qid, 'question': q[1], 'answers': answers_dict})
    
    return render_template('solve_quiz.html', quiz_id=quiz_id, questions=questions_data)


@app.route('/api/solve_quiz/<int:quiz_id>', methods=['POST'])
def solve_quiz(quiz_id):
    db = get_db()
    c = db.cursor()

    # Pobierz poprawne odpowiedzi
    c.execute('SELECT id, correct_answer FROM questions WHERE quiz_id = ?', (quiz_id,))
    questions = c.fetchall()
    correct_answers = {qid: correct for qid, correct in questions}

    user_answers = request.json  # Odpowiedzi użytkownika z formularza

    correct_count = 0
    for qid, correct_answer in correct_answers.items():
        user_answer = user_answers.get(f'question-{qid}')
        if user_answer == correct_answer:
            correct_count += 1

    total_questions = len(correct_answers)
    score = (correct_count / total_questions) * 100

    return jsonify({
        'success': True,
        'score': score
    })
if __name__ == '__main__':
    app.run(debug=True)

