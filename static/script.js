document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

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
