$(document).ready(function() {
    const token = getCookie('jwt');
    if (token) {
        $.ajax({
            type: 'GET',
            url: '/verify_token',  // Your server-side route to verify the token
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(data, status) {
                console.log(data.payload);
                displayUsername(data.payload.username);
                displaySignout();
                $(".auth-buttons").hide();  // Hiding the buttons if response is 'OK'
                $(".modal").hide();

            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Unexpected error: ', textStatus, errorThrown);
                if (jqXHR.status == 401) {
                    console.log(jqXHR.responseJSON.error);  // Log the error message returned from the server for 401 error
                }
                if (jqXHR.status == 400) {
                    console.log(jqXHR.responseJSON.error);  // Log the error message returned from the server for 400 error
                }
                alert('Please Sign In');
            }
        });
    } else {
        alert('Please Sign In');
    }
});


function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
}

function displayUsername(username) {
    // Update the text content of the usernameDisplay element with the username
    document.getElementById('usernameDisplay').textContent = username;
}

function setJwtCookie(jwt) {
// Set the JWT as a cookie
document.cookie = `jwt=${jwt}; samesite=strict; secure`; // Add `secure` attribute for HTTPS, remove it for local development if you don't have HTTPS
}

function submitSignUp() {
    const username = document.getElementById("signUpUsername").value;
    const password = document.getElementById("signUpPassword").value;

    console.log("Sign Up - Username: " + username + ", Password: " + password);

    $.ajax({
        url: '/sign_up',
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json',  // Expect a JSON response from server
        data: JSON.stringify({ // Convert the JavaScript object to a JSON string
            "username": username,
            "password": password
        }),
        success: function(response) {
            console.log(response); // Log the response from the server to the console
            if (response.msg === 'OK'){
                $(".auth-buttons").hide();  // Hiding the buttons if response is 'OK'
                $(".modal").hide();
                alert('sign up successfully')
                displayUsername(username);
                displaySignout()
                setJwtCookie(response.jwt_token)
            }else {
                alert('Sign up failed: ' + response.msg);  // Assume an error message is returned in the response
            }
        },
        error: function(error) {
            console.error(error); // Log any errors to the console
        }
    });
}

function submitSignIn() {
    const username = document.getElementById("signInUsername").value;
    const password = document.getElementById("signInPassword").value;

    console.log("Sign In - Username: " + username + ", Password: " + password);

    $.ajax({
        url: '/sign_in', // Replace with the URL of your backend endpoint
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        dataType: 'json',  // Expect a JSON response from server
        data: JSON.stringify({ // Convert the JavaScript object to a JSON string
            "username": username,
            "password": password
        }),
        success: function(response) {
            console.log(response); // Log the response from the server to the console
            if (response.msg === 'OK'){
                $(".auth-buttons").hide();  // Hiding the buttons if response is 'OK'
                $(".modal").hide();
                alert('sign in successfully')
                displayUsername(username);
                displaySignout()
                setJwtCookie(response.jwt_token)
            }else {
                alert('Sign in failed: ' + response.msg);  // Assume an error message is returned in the response
            }
        },
        error: function(error) {
            console.error(error); // Log any errors to the console
        }
    });
}

function displaySignout(){
    document.getElementById('logoutButton').style.display = 'block';
}


function logout() {
    console.log('Logged out');
    document.getElementById('usernameDisplay').textContent = '';
    document.getElementById('logoutButton').style.display = 'none';
    $(".auth-buttons").show();
    document.cookie = "jwt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload();
}