document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    
    // Handle login form submission
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
    
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        // Custom validation: Check if fields are empty
        if (username === "" || password === "") {
            errorMessage.textContent = "Username or password is missing!";
            errorMessage.style.color = "red";
            return; // Stop execution
        }
    
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
                // Display error message
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

function updateStudent(studentId, button) {
    let row = document.getElementById("student-" + studentId);
    let newUsername = row.querySelector(".edit-username").innerText.trim();

    if (newUsername === "") {
        alert("Username cannot be empty!");
        return;
    }

    fetch('/update-student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: studentId, username: newUsername })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Student updated successfully!");
        } else {
            alert("Error updating student: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}

function deleteStudent(studentId) {
    if (!confirm("Are you sure you want to delete this student?")) {
        return;
    }

    fetch('/delete-student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: studentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Student deleted successfully!");
            document.getElementById("student-" + studentId).remove(); // Remove row from table
        } else {
            alert("Error deleting student: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}
async function redeemItem(itemName) {
    const response = await fetch('/redeem-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: itemName })
    });

    const result = await response.json();

    if (result.success) {
        alert(result.message);
        document.getElementById("user-points").textContent = result.remaining_points;
    } else {
        alert(result.message);
    }
}

async function addStudent() {
    let username = document.getElementById('new-username').value;
    let password = document.getElementById('new-password').value;
    let points = document.getElementById('new-points').value; // ✅ Get points value

    if (!username || !password || !points) {
        alert("All fields are required!");
        return;
    }

    let response = await fetch('/add_student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, points }) // ✅ Send points
    });

    let result = await response.json();
    alert(result.message);
    if (result.success) location.reload(); // ✅ Reload to update student list
}

async function searchStudents() {
    let query = document.getElementById("search-input").value;

    let response = await fetch("/search_students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    });

    let result = await response.json();

    // ✅ Clear the table before inserting new search results
    let studentList = document.getElementById("student-list");
    studentList.innerHTML = "";

    // ✅ Populate table with search results
    result.students.forEach(student => {
        let row = `
            <tr id="student-${student[0]}">
                <td>${student[0]}</td>
                <td contenteditable="true" class="edit-username">${student[1]}</td>
                <td>${student[2]}</td>
                <td class="actions">
                    <button class="update-btn" onclick="updateStudent(${student[0]}, this)">Update</button>
                    <button class="delete-btn" onclick="deleteStudent(${student[0]})">Delete</button>
                </td>
            </tr>`;
        studentList.innerHTML += row;
    });
}


