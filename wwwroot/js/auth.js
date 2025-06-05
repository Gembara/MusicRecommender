// Глобальні змінні для авторизації
let currentUser = null;

// Перевірка стану авторизації при завантаженні сторінки
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
});

// Перевірка поточного стану авторизації
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/Auth/current');
        const data = await response.json();
        
        if (data.success && data.isLoggedIn) {
            currentUser = {
                userId: data.userId,
                userName: data.userName
            };
            updateUIForLoggedInUser();
        } else {
            currentUser = null;
            updateUIForLoggedOutUser();
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        currentUser = null;
        updateUIForLoggedOutUser();
    }
}

// Вхід користувача
async function login(userName, email = '') {
    try {
        const response = await fetch('/api/Auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                userName: userName,
                email: email
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = {
                userId: data.userId,
                userName: data.userName
            };
            updateUIForLoggedInUser();
            showNotification(`Ласкаво просимо, ${data.userName}!`, 'success');
            return true;
        } else {
            showNotification('Помилка входу: ' + data.message, 'error');
            return false;
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Помилка при вході в систему', 'error');
        return false;
    }
}

// Вихід користувача
async function logout() {
    try {
        const response = await fetch('/api/Auth/logout', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = null;
            updateUIForLoggedOutUser();
            showNotification('Ви успішно вийшли з системи', 'success');
        } else {
            showNotification('Помилка виходу: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Помилка при виході з системи', 'error');
    }
}

// Оновлення UI для авторизованого користувача
function updateUIForLoggedInUser() {
    if (!currentUser) return;
    
    // Оновити навігацію
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        // Видалити існуючі елементи авторизації
        const existingAuthItems = navbar.querySelectorAll('.auth-item');
        existingAuthItems.forEach(item => item.remove());
        
        // Додати інформацію про користувача
        const userItem = document.createElement('li');
        userItem.className = 'nav-item dropdown auth-item';
        userItem.innerHTML = `
            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user"></i> ${currentUser.userName}
            </a>
            <ul class="dropdown-menu">
                <li><span class="dropdown-item-text">ID: ${currentUser.userId}</span></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" onclick="logout()">Вийти</a></li>
            </ul>
        `;
        navbar.appendChild(userItem);
    }
    
    // Показати модальне вікно входу якщо воно відкрите
    const loginModal = document.getElementById('loginModal');
    if (loginModal && window.bootstrap) {
        const modal = bootstrap.Modal.getInstance(loginModal);
        if (modal) {
            modal.hide();
        }
    }
    
    // Оновити кнопки додавання в улюблені
    updateFavoriteButtons();
}

// Оновлення UI для неавторизованого користувача
function updateUIForLoggedOutUser() {
    // Оновити навігацію
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        // Видалити існуючі елементи авторизації
        const existingAuthItems = navbar.querySelectorAll('.auth-item');
        existingAuthItems.forEach(item => item.remove());
        
        // Додати кнопку входу
        const loginItem = document.createElement('li');
        loginItem.className = 'nav-item auth-item';
        loginItem.innerHTML = `
            <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#loginModal">
                <i class="fas fa-sign-in-alt"></i> Увійти
            </a>
        `;
        navbar.appendChild(loginItem);
    }
    
    // Оновити кнопки додавання в улюблені
    updateFavoriteButtons();
}

// Оновлення кнопок улюблених треків
function updateFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(btn => {
        if (currentUser) {
            btn.style.display = 'inline-block';
        } else {
            btn.style.display = 'none';
        }
    });
}

// Отримати поточного користувача
function getCurrentUser() {
    return currentUser;
}

// Перевірити чи користувач авторизований
function isLoggedIn() {
    return currentUser !== null;
}

// Показати модальне вікно входу
function showLoginModal() {
    const loginModal = document.getElementById('loginModal');
    if (loginModal && window.bootstrap) {
        const modal = new bootstrap.Modal(loginModal);
        modal.show();
    }
}

// Обробка форми входу
function handleLoginForm() {
    const userName = document.getElementById('loginUserName')?.value?.trim();
    const email = document.getElementById('loginEmail')?.value?.trim();
    
    if (!userName) {
        showNotification('Будь ласка, введіть ім\'я користувача', 'error');
        return;
    }
    
    login(userName, email);
}

// Функція для показу повідомлень (якщо не існує)
function showNotification(message, type = 'info') {
    // Створюємо контейнер для повідомлень якщо його немає
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
    }
    
    // Створюємо повідомлення
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show`;
    notification.style.cssText = `
        margin-bottom: 10px;
        min-width: 300px;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Автоматично видалити через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Експорт функцій глобально
window.getCurrentUser = getCurrentUser;
window.isLoggedIn = isLoggedIn;
window.showLoginModal = showLoginModal;
window.showNotification = showNotification;
window.login = login;
window.logout = logout; 