document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
    
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
    
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
    
            const result = await response.json();
    
            if (result.success) {
                // Redirect to the appropriate page
                window.location.href = result.redirect_url;
            } else {
                // Display error message only if it exists
                errorMessage.textContent = result.message || 'Invalid login credentials.';
            }
        } catch (error) {
            console.error('Error during login:', error);
            errorMessage.textContent = 'An unexpected error occurred. Please try again later.';
        }
    });
    


    togglePassword.addEventListener('click', () => {
        const isPasswordHidden = passwordInput.type === 'password';
        passwordInput.type = isPasswordHidden ? 'text' : 'password';
        togglePassword.textContent = isPasswordHidden ? '🙈' : '👁️';
    });


    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
        } else {
            document.getElementById('error-message').textContent = result.message;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('error-message').textContent = 'Unable to connect to the server.';
    }
});
