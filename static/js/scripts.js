console.log('scripts.js is loaded');

// Handle registration form
document.getElementById('register-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Rejestracja zakończona pomyślnie.');
            window.location.href = '/login';
        } else {
            alert('Wystąpił błąd podczas rejestracji: ' + data.message);
        }
    })
    .catch(error => {
        alert('Wystąpił błąd: ' + error.message);
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Handle login form
document.getElementById('login-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Logowanie zakończone pomyślnie.');
            window.location.href = '/';
        } else {
            alert('Błędna nazwa użytkownika lub hasło: ' + data.message);
        }
    })
    .catch(error => {
        alert('Wystąpił błąd: ' + error.message);
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Handle task addition form
document.getElementById('add-task-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const dueDate = document.getElementById('due-date').value;

    console.log('Formularz wysłany:', { title, description, dueDate });

    fetch('/api/add_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, due_date: dueDate })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Odpowiedź JSON:', data);
        if (data.success) {
            alert('Zadanie dodane pomyślnie.');
            window.location.href = '/task_info';
        } else {
            alert('Wystąpił błąd podczas dodawania zadania: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Wystąpił problem z operacją fetch:', error);
    });
});

// Fetch task list
function fetchTaskList() {
    fetch('/api/task_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const taskList = document.getElementById('task-list');
                taskList.innerHTML = '';

                data.tasks.forEach(task => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-task-id', task.id);

                    const title = document.createElement('td');
                    title.textContent = task.title;

                    const description = document.createElement('td');
                    description.textContent = task.description;

                    const dueDate = document.createElement('td');
                    dueDate.textContent = task.due_date;

                    const isCompleted = document.createElement('td');
                    isCompleted.textContent = task.is_completed ? 'Tak' : 'Nie';

                    const editButton = document.createElement('button');
                    editButton.textContent = 'Edytuj';
                    editButton.className = 'edit-task';

                    const deleteButton = document.createElement('button');
                    deleteButton.textContent = 'Usuń';
                    deleteButton.className = 'delete-task';

                    const actionsTd = document.createElement('td');
                    actionsTd.appendChild(editButton);
                    actionsTd.appendChild(deleteButton);

                    tr.appendChild(title);
                    tr.appendChild(description);
                    tr.appendChild(dueDate);
                    tr.appendChild(isCompleted);
                    tr.appendChild(actionsTd);

                    taskList.appendChild(tr);
                });

                addEventListeners();
            } else {
                alert('Wystąpił błąd podczas pobierania zadań: ' + data.error);
            }
        })
        .catch(error => console.error('Wystąpił problem z operacją fetch:', error));
}

// Add event listeners for task actions
function addEventListeners() {
    document.querySelectorAll('.edit-task').forEach(button => {
        button.addEventListener('click', function () {
            const taskRow = this.closest('tr');
            const taskId = taskRow.getAttribute('data-task-id');

            const title = taskRow.children[0].textContent;
            const description = taskRow.children[1].textContent;
            const dueDate = taskRow.children[2].textContent;
            const isCompleted = taskRow.children[3].textContent === 'Tak';

            const newTitle = prompt("Edytuj tytuł:", title);
            const newDescription = prompt("Edytuj opis:", description);
            const newDueDate = prompt("Edytuj datę zakończenia:", dueDate);
            const newIsCompleted = confirm("Czy zadanie jest ukończone?") ? true : false;

            fetch(`/api/edit_task/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    title: newTitle || title, 
                    description: newDescription || description,
                    due_date: newDueDate || dueDate,
                    is_completed: newIsCompleted
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Zadanie zostało zaktualizowane.');
                    window.location.reload();
                } else {
                    alert('Wystąpił błąd podczas aktualizacji zadania: ' + data.error);
                }
            })
            .catch(error => console.error('Wystąpił problem z operacją fetch:', error));
        });
    });

    document.querySelectorAll('.delete-task').forEach(button => {
        button.addEventListener('click', function () {
            if (!confirm("Czy na pewno chcesz usunąć to zadanie?")) return;

            const taskRow = this.closest('tr');
            const taskId = taskRow.getAttribute('data-task-id');

            fetch(`/delete_task/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Zadanie zostało usunięte.');
                    window.location.reload();
                } else {
                    alert('Wystąpił błąd podczas usuwania zadania: ' + data.error);
                }
            })
            .catch(error => console.error('Wystąpił problem z operacją fetch:', error));
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM wczytany');
    if (document.getElementById('task-list')) {
        fetchTaskList();
    }
});

// Handle logout
document.getElementById('logout-button')?.addEventListener('click', function() {
    fetch('/logout', {
        method: 'GET'
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('Wystąpił błąd podczas wylogowywania.');
        }
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Add dynamic quiz questions
document.getElementById('add-question')?.addEventListener('click', function() {
    const container = document.getElementById('questions-container');
    const questionCount = container.getElementsByClassName('question-item').length + 1;

    const questionItem = document.createElement('div');
    questionItem.className = 'question-item';

    questionItem.innerHTML = `
        <label for="question-${questionCount}">Pytanie ${questionCount}:</label>
        <input type="text" id="question-${questionCount}" name="questions[${questionCount - 1}][question]" required>

        <label>Odpowiedzi:</label>
        <input type="text" name="questions[${questionCount - 1}][answers][A]" placeholder="Odpowiedź A" required>
        <input type="text" name="questions[${questionCount - 1}][answers][B]" placeholder="Odpowiedź B" required>
        <input type="text" name="questions[${questionCount - 1}][answers][C]" placeholder="Odpowiedź C" required>
        <input type="text" name="questions[${questionCount - 1}][answers][D]" placeholder="Odpowiedź D" required>

        <label for="correct-${questionCount}">Poprawna odpowiedź:</label>
        <select id="correct-${questionCount}" name="questions[${questionCount - 1}][correct]" required>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
        </select>
    `;

    container.appendChild(questionItem);
});

// Handle quiz creation form
document.getElementById('create-quiz-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const quizData = Object.fromEntries(formData.entries());
    quizData.questions = [];

    const questionItems = document.querySelectorAll('.question-item');
    questionItems.forEach((item, index) => {
        const question = {
            question: formData.get(`questions[${index}][question]`),
            answers: {
                A: formData.get(`questions[${index}][answers][A]`),
                B: formData.get(`questions[${index}][answers][B]`),
                C: formData.get(`questions[${index}][answers][C]`),
                D: formData.get(`questions[${index}][answers][D]`)
            },
            correct: formData.get(`questions[${index}][correct]`)
        };
        quizData.questions.push(question);
    });

    fetch('/api/create_quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(quizData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Quiz stworzony pomyślnie.');
            window.location.href = '/';
        } else {
            alert('Wystąpił błąd podczas tworzenia quizu: ' + data.message);
        }
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Fetch quiz list
function fetchQuizList() {
    fetch('/api/quiz_list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const quizList = document.getElementById('quiz-list');
                quizList.innerHTML = '';

                data.quizzes.forEach(quiz => {
                    const tr = document.createElement('tr');

                    const titleCell = document.createElement('td');
                    const a = document.createElement('a');
                    a.href = `/solve_quiz/${quiz.id}`;
                    a.textContent = quiz.title;
                    titleCell.appendChild(a);

                    const questionCountCell = document.createElement('td');
                    questionCountCell.textContent = quiz.question_count || '0';

                    tr.appendChild(titleCell);
                    tr.appendChild(questionCountCell);

                    quizList.appendChild(tr);
                });
            } else {
                alert('Wystąpił błąd podczas pobierania quizów: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching quiz list:', error);
            alert('Wystąpił błąd podczas pobierania listy quizów.');
        });
}

// Handle quiz solving
document.getElementById('solve-quiz-form')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const quiz_id = document.getElementById('quiz-id').value;
    const userAnswers = {};
    
    document.querySelectorAll('input[type="radio"]:checked').forEach(input => {
        userAnswers[input.name] = input.value;
    });

    fetch(`/solve_quiz/${quiz_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userAnswers)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const totalQuestions = Object.keys(userAnswers).length;
            const scorePercentage = (data.score / totalQuestions) * 100;
            alert(`Quiz submitted successfully! Your score is: ${scorePercentage.toFixed(2)}%`);
        } else {
            alert('Failed to submit quiz');
        }
    })
    .catch(error => console.error('Error:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('quiz-list')) {
        fetchQuizList();
    }
});
