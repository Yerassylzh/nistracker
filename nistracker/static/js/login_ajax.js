function checkLoginStatus() {
    $.ajax({
        url: "/",
        method: "GET",
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            action: "check status",
        },
        success: function(response) {
            if (response.error) {
                alert('Error: ' + JSON.stringify(response.errors));
                return;
            }

            if (response.status === "success") {
                $("#login-status").attr("src", "done.gif");
                window.location.href = "{% url 'homepage:home' %}";
            } else if (response.status === "failure") {
                alert(response.message);
            } else if (! ($("#login-status").attr("src").endsWith("loading.gif")) ) {
                $("#login-status").attr("src", "loading.gif");
            } else {
                console.log("Got an issue after successfully checking login status");
            }
        },
        error: function(xhr, status, error) {
            console.log("Error: " + error);
        }
    });
}

function startLogin() {
    $.ajax({
        url: "/",
        method: "POST",
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function(response) {
            setInterval(checkLoginStatus, 200);
        },
        error: function(xhr, status, error) {
            console.log("Error: " + error);
        }
    });
}

$(document).ready(function() {
    $("#loginForm").submit(function(event) {
        event.preventDefault(); // Prevent the default form submission
        startLogin(); // Start the login process });
    })
});
