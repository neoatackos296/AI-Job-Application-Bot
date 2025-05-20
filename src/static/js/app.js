// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registered');
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// Bot Control
class BotController {
    constructor() {
        this.running = false;
        this.setupEventListeners();
        this.checkStatus();
    }

    setupEventListeners() {
        const toggleButton = document.getElementById('toggleBot');
        if (toggleButton) {
            toggleButton.addEventListener('click', () => this.toggleBot());
        }

        // Auto-logout timer
        document.addEventListener('mousemove', () => this.resetInactivityTimer());
        document.addEventListener('keypress', () => this.resetInactivityTimer());
    }

    toggleBot() {
        const endpoint = this.running ? '/stop_bot' : '/start_bot';
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            this.running = !this.running;
            this.updateBotStatus();
            showNotification(data.message, 'success');
        })
        .catch(error => {
            showNotification('Failed to toggle bot', 'error');
        });
    }

    checkStatus() {
        fetch('/bot_status')
            .then(response => response.json())
            .then(data => {
                this.running = data.running;
                this.updateBotStatus();
            });
    }

    updateBotStatus() {
        const toggleButton = document.getElementById('toggleBot');
        if (toggleButton) {
            toggleButton.classList.toggle('active', this.running);
            toggleButton.querySelector('i').textContent = 
                this.running ? 'stop' : 'play_arrow';
        }
    }

    resetInactivityTimer() {
        if (this.inactivityTimeout) {
            clearTimeout(this.inactivityTimeout);
        }
        this.inactivityTimeout = setTimeout(() => {
            window.location.href = '/logout';
        }, 15 * 60 * 1000); // 15 minutes
    }
}

// Form Handling
class PreferencesManager {
    constructor() {
        this.form = document.getElementById('preferencesForm');
        if (this.form) {
            this.setupFormHandling();
        }
    }

    setupFormHandling() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Location tags
        const newLocation = document.getElementById('newLocation');
        if (newLocation) {
            newLocation.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.addLocation(e.target.value);
                    e.target.value = '';
                }
            });
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(this.form);
        const locations = Array.from(document.querySelectorAll('.location-tags .tag'))
            .map(tag => tag.textContent.trim());
        
        const data = {
            job_role: formData.get('job_role'),
            experience: formData.get('experience'),
            locations: locations,
            salary_range: [
                parseInt(formData.get('salaryMin')),
                parseInt(formData.get('salaryMax'))
            ]
        };

        fetch('/update_preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            showNotification('Preferences updated successfully', 'success');
        })
        .catch(error => {
            showNotification('Failed to update preferences', 'error');
        });
    }

    addLocation(location) {
        if (!location) return;
        
        const locationTags = document.querySelector('.location-tags');
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.innerHTML = `
            ${location}
            <i class="material-icons" onclick="this.parentElement.remove()">close</i>
        `;
        locationTags.insertBefore(tag, document.getElementById('newLocation'));
    }
}

// Notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new BotController();
    new PreferencesManager();
});
