/**
 * Notification Manager for StackScout
 * Handles in-app notifications and user preferences
 */

class NotificationManager {
    constructor() {
        this.notificationCount = 0;
        this.notificationContainer = null;
        this.notificationBell = null;
        this.initialize();
    }

    initialize() {
        // Create notification elements
        this.createNotificationUI();
        
        // Load initial notifications
        this.loadNotifications();
        
        // Set up periodic refresh
        setInterval(() => this.loadNotifications(), 30000); // Refresh every 30 seconds
    }

    createNotificationUI() {
        // Create notification bell in header
        const header = document.querySelector('header');
        if (header) {
            this.notificationBell = document.createElement('div');
            this.notificationBell.className = 'notification-bell';
            this.notificationBell.innerHTML = `
                <button class="relative p-2 text-gray-600 hover:text-blue-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                    </svg>
                    <span class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full notification-count" style="display: none;">0</span>
                </button>
            `;
            
            // Add to header navigation
            const nav = header.querySelector('nav');
            if (nav) {
                nav.appendChild(this.notificationBell);
            }

            // Create notification dropdown
            this.notificationContainer = document.createElement('div');
            this.notificationContainer.className = 'notification-dropdown hidden absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg z-50';
            this.notificationContainer.innerHTML = `
                <div class="p-4 border-b">
                    <h3 class="text-lg font-semibold text-gray-900">Notifications</h3>
                </div>
                <div class="max-h-96 overflow-y-auto">
                    <div class="notification-list p-2"></div>
                </div>
                <div class="p-4 border-t">
                    <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mark-all-read">
                        Mark All as Read
                    </button>
                </div>
            `;

            document.body.appendChild(this.notificationContainer);

            // Add event listeners
            this.addEventListeners();
        }
    }

    addEventListeners() {
        // Toggle notification dropdown
        this.notificationBell.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleNotifications();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.notificationContainer.contains(e.target) && 
                !this.notificationBell.contains(e.target)) {
                this.hideNotifications();
            }
        });

        // Mark all as read
        const markAllButton = this.notificationContainer.querySelector('.mark-all-read');
        if (markAllButton) {
            markAllButton.addEventListener('click', () => this.markAllAsRead());
        }
    }

    toggleNotifications() {
        this.notificationContainer.classList.toggle('hidden');
        if (!this.notificationContainer.classList.contains('hidden')) {
            this.loadNotifications();
        }
    }

    hideNotifications() {
        this.notificationContainer.classList.add('hidden');
    }

    async loadNotifications() {
        try {
            const response = await fetch('/notifications/', {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });
            
            if (response.ok) {
                const notifications = await response.json();
                this.renderNotifications(notifications);
                this.updateNotificationCount(notifications.filter(n => !n.is_read).length);
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    renderNotifications(notifications) {
        const list = this.notificationContainer.querySelector('.notification-list');
        if (!list) return;

        if (notifications.length === 0) {
            list.innerHTML = '<p class="text-center text-gray-500 py-4">No notifications</p>';
            return;
        }

        list.innerHTML = notifications.map(notification => `
            <div class="notification-item p-3 border-b hover:bg-gray-50 cursor-pointer ${notification.is_read ? 'opacity-60' : ''}" 
                 data-id="${notification.id}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-900">${this.escapeHtml(notification.title)}</h4>
                        <p class="text-sm text-gray-600">${this.escapeHtml(notification.message)}</p>
                        <p class="text-xs text-gray-400 mt-1">${new Date(notification.created_at).toLocaleString()}</p>
                    </div>
                    ${!notification.is_read ? '<span class="w-2 h-2 bg-blue-600 rounded-full ml-2 mt-1"></span>' : ''}
                </div>
            </div>
        `).join('');

        // Add click handlers
        list.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => this.markAsRead(item.dataset.id));
        });
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/notifications/${notificationId}/read`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });
            
            if (response.ok) {
                this.loadNotifications(); // Refresh notifications
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            // This would require a new endpoint for batch operations
            // For now, we'll mark each notification individually
            const notifications = await this.getNotifications();
            for (const notification of notifications.filter(n => !n.is_read)) {
                await this.markAsRead(notification.id);
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }

    updateNotificationCount(count) {
        this.notificationCount = count;
        const countElement = this.notificationBell.querySelector('.notification-count');
        if (countElement) {
            if (count > 0) {
                countElement.textContent = count > 99 ? '99+' : count;
                countElement.style.display = 'block';
            } else {
                countElement.style.display = 'none';
            }
        }
    }

    getToken() {
        // Get JWT token from localStorage or cookies
        return localStorage.getItem('auth_token') || '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async getNotifications() {
        try {
            const response = await fetch('/notifications/', {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });
            return response.ok ? await response.json() : [];
        } catch (error) {
            console.error('Error getting notifications:', error);
            return [];
        }
    }
}

// Initialize notification manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');
    if (token) {
        window.notificationManager = new NotificationManager();
    }
});
