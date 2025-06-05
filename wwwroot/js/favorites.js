document.addEventListener('DOMContentLoaded', function() {
    // Функція для додавання треку в улюблені
    async function addToFavorites(spotifyTrackId, title, artist, imageUrl) {
        const user = getCurrentUser();
        if (!user) {
            showNotification('Спочатку увійдіть в систему', 'error');
            showLoginModal();
            return;
        }

        try {
            const response = await fetch('/api/Favorites/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    spotifyTrackId: spotifyTrackId,
                    title: title,
                    artist: artist,
                    imageUrl: imageUrl
                })
            });

            if (response.ok) {
                showNotification('Трек додано в улюблені!', 'success');
                
                // Записуємо взаємодію з треком як лайк (рейтинг 5)
                await recordInteraction(spotifyTrackId, 5, true);
                
                // Оновлюємо UI
                updateFavoriteButton(spotifyTrackId, true);
            } else {
                const errorData = await response.json();
                showNotification('Помилка: ' + (errorData.message || 'Не вдалося додати в улюблені'), 'error');
            }
        } catch (error) {
            console.error('Error adding to favorites:', error);
            showNotification('Помилка при додаванні в улюблені', 'error');
        }
    }

    // Функція для видалення треку з улюблених
    async function removeFromFavorites(spotifyTrackId) {
        const user = getCurrentUser();
        if (!user) {
            showNotification('Спочатку увійдіть в систему', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/Favorites/remove/${spotifyTrackId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showNotification('Трек видалено з улюблених', 'success');
                
                // Записуємо взаємодію з треком як дизлайк (рейтинг 1)
                await recordInteraction(spotifyTrackId, 1, false);
                
                // Оновлюємо UI
                updateFavoriteButton(spotifyTrackId, false);
            } else {
                const errorData = await response.json();
                showNotification('Помилка: ' + (errorData.message || 'Не вдалося видалити з улюблених'), 'error');
            }
        } catch (error) {
            console.error('Error removing from favorites:', error);
            showNotification('Помилка при видаленні з улюблених', 'error');
        }
    }

    // Записати взаємодію користувача з треком для ML
    async function recordInteraction(spotifyTrackId, rating, isLiked) {
        const user = getCurrentUser();
        if (!user) return;

        try {
            await fetch('/Recommendation/RecordInteraction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userId: user.userId,
                    trackId: spotifyTrackId,
                    interactionType: isLiked ? 2 : 3, // Liked = 2, Disliked = 3
                    rating: rating,
                    playDuration: 0,
                    isSkipped: false,
                    isLiked: isLiked
                })
            });
        } catch (error) {
            console.error('Error recording interaction:', error);
        }
    }

    // Оновити кнопку улюблених для конкретного треку
    function updateFavoriteButton(spotifyTrackId, isFavorite) {
        const buttons = document.querySelectorAll(`[data-track-id="${spotifyTrackId}"]`);
        buttons.forEach(button => {
            if (button.classList.contains('favorite-btn')) {
                const icon = button.querySelector('i');
                
                // Додаємо анімацію
                button.classList.add('animating');
                setTimeout(() => {
                    button.classList.remove('animating');
                }, 600);
                
                if (isFavorite) {
                    icon.className = 'fas fa-heart';
                    icon.style.color = '#dc3545';
                    button.title = 'Видалити з улюблених';
                    button.onclick = () => removeFromFavorites(spotifyTrackId);
                } else {
                    icon.className = 'far fa-heart';
                    icon.style.color = '';
                    button.title = 'Додати в улюблені';
                    button.onclick = () => {
                        const item = button.closest('.search-item, .recommendation-item');
                        if (item) {
                            const title = item.querySelector('.search-item-title, .recommendation-title')?.textContent || '';
                            const artist = item.querySelector('.search-item-subtitle, .recommendation-artist')?.textContent || '';
                            const imageElement = item.querySelector('.search-item-image, .recommendation-image');
                            let imageUrl = '';
                            if (imageElement) {
                                imageUrl = imageElement.style.backgroundImage
                                    ?.replace(/^url\(['"](.+)['"]\)$/, '$1') || 
                                    imageElement.src || '';
                            }
                            addToFavorites(spotifyTrackId, title, artist, imageUrl);
                        }
                    };
                }
            }
        });
    }

    // Перевірити статус улюбленого для треку
    async function checkFavoriteStatus(spotifyTrackId) {
        const user = getCurrentUser();
        if (!user) return false;

        try {
            const response = await fetch(`/api/Favorites/check/${spotifyTrackId}`);
            if (response.ok) {
                const data = await response.json();
                return data.isFavorite;
            }
        } catch (error) {
            console.error('Error checking favorite status:', error);
        }
        return false;
    }

    // Оновити всі кнопки улюблених на сторінці
    async function updateAllFavoriteButtons() {
        const user = getCurrentUser();
        if (!user) {
            // Приховати всі кнопки якщо користувач не авторизований
            const favoriteButtons = document.querySelectorAll('.favorite-btn');
            favoriteButtons.forEach(btn => btn.style.display = 'none');
            return;
        }

        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        for (const button of favoriteButtons) {
            const spotifyTrackId = button.getAttribute('data-track-id');
            if (spotifyTrackId) {
                const isFavorite = await checkFavoriteStatus(spotifyTrackId);
                updateFavoriteButton(spotifyTrackId, isFavorite);
                button.style.display = 'inline-block';
            }
        }
    }

    // Функція для показу повідомлень (fallback якщо не існує в auth.js)
    if (typeof showNotification === 'undefined') {
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
    }

    // Слухач подій для оновлення кнопок після авторизації
    setTimeout(() => {
        updateAllFavoriteButtons();
    }, 100);

    // Експортуємо функції глобально
    window.addToFavorites = addToFavorites;
    window.removeFromFavorites = removeFromFavorites;
    window.checkFavoriteStatus = checkFavoriteStatus;
    window.updateFavoriteButton = updateFavoriteButton;
    window.updateAllFavoriteButtons = updateAllFavoriteButtons;

    // Глобальна функція для оновлення кнопок (викликається з auth.js)
    window.updateFavoriteButtons = updateAllFavoriteButtons;
}); 