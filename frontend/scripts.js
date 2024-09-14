document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.user_type) {
                    window.location.href = `/${data.user_type}`;
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Error logging in:', error));
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const username = document.getElementById('new-username').value;
            const password = document.getElementById('new-password').value;
            const userType = document.getElementById('user-type').value;

            fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password, user_type: userType })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.message === 'User registered successfully') {
                    window.location.href = '/';
                }
            })
            .catch(error => console.error('Error signing up:', error));
        });
    }
});
