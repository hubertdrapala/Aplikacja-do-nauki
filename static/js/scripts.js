console.log('scripts.js is loaded');

// Obsługa formularza rejestracji
document.getElementById('register-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, username, password })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw new Error(data.message); });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Rejestracja zakończona pomyślnie.');
            window.location.href = '/login';
        } else {
            alert('Wystąpił błąd podczas rejestracji.');
        }
    })
    .catch(error => {
        alert('Wystąpił błąd: ' + error.message);
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Obsługa formularza logowania
document.getElementById('login-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw new Error(data.message); });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Logowanie zakończone pomyślnie.');
            window.location.href = '/';
        } else {
            alert('Błędna nazwa użytkownika lub hasło.');
        }
    })
    .catch(error => {
        alert('Wystąpił błąd: ' + error.message);
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Obsługa formularza dodawania zadania
// Obsługa formularza dodawania zadania
document.getElementById('add-task-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const dueDate = document.getElementById('due-date').value;

    console.log('Formularz wysłany:', { title, description, dueDate }); // Dodane logowanie

    fetch('/api/add_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description, due_date: dueDate })
    })
    .then(response => {
        console.log('Odpowiedź z serwera:', response); // Dodane logowanie
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Odpowiedź JSON:', data); // Dodane logowanie
        if (data.success) {
            alert('Zadanie dodane pomyślnie.');
            window.location.href = '/';
        } else {
            alert('Wystąpił błąd podczas dodawania zadania.');
        }
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});

// Pobieranie listy zadań
function fetchTaskList() {
    fetch('/api/task_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const taskList = document.getElementById('task-list');
                taskList.innerHTML = '';

                data.tasks.forEach(task => {
                    const tr = document.createElement('tr');

                    const title = document.createElement('td');
                    const a = document.createElement('a');
                    a.href = `/task-detail/${task.id}`;
                    a.textContent = task.title;
                    title.appendChild(a);

                    const description = document.createElement('td');
                    description.textContent = task.description;

                    const dueDate = document.createElement('td');
                    dueDate.textContent = task.due_date;

                    const isCompleted = document.createElement('td');
                    isCompleted.textContent = task.is_completed ? 'Tak' : 'Nie';

                    tr.appendChild(title);
                    tr.appendChild(description);
                    tr.appendChild(dueDate);
                    tr.appendChild(isCompleted);
                    taskList.appendChild(tr);
                });
            } else {
                alert('Wystąpił błąd podczas pobierania zadań.');
            }
        })
        .catch(error => console.error('Error fetching task list:', error));
}

if (document.getElementById('task-list')) {
    fetchTaskList();
}

// Obsługa wylogowania
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

// Obsługa formularza dodawania wydatku/przychodu
document.getElementById('add-finance-form')?.addEventListener('submit', function(event) {
    event.preventDefault();

    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;
    const date = document.getElementById('date').value;
    const type = document.getElementById('type').value;

    console.log('Formularz wysłany:', { amount, description, date, type });

    fetch('/api/add_finance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount, description, date, type })
    })
    .then(response => {
        console.log('Odpowiedź z serwera:', response);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Odpowiedź JSON:', data);
        if (data.success) {
            alert('Transakcja dodana pomyślnie.');
            window.location.href = '/';
        } else {
            alert('Wystąpił błąd podczas dodawania transakcji.');
        }
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
});



// Funkcja do pobierania listy finansów
function fetchFinanceList() {
    fetch('/api/finance_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const financeList = document.getElementById('finance-list');
                financeList.innerHTML = '';

                data.finances.forEach(finance => {
                    const tr = document.createElement('tr');

                    const amount = document.createElement('td');
                    amount.textContent = finance.amount;

                    const description = document.createElement('td');
                    description.textContent = finance.description;

                    const date = document.createElement('td');
                    date.textContent = finance.date;

                    const type = document.createElement('td');
                    type.textContent = finance.type;

                    tr.appendChild(amount);
                    tr.appendChild(description);
                    tr.appendChild(date);
                    tr.appendChild(type);
                    financeList.appendChild(tr);
                });
            } else {
                alert('Wystąpił błąd podczas pobierania finansów.');
            }
        })
        .catch(error => console.error('Error fetching finance list:', error));
}

// Wywołanie funkcji fetchFinanceList jeśli element finance-list jest obecny
if (document.getElementById('finance-list')) {
    fetchFinanceList();
}