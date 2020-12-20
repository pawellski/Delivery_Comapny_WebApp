document.addEventListener('DOMContentLoaded', function (event) {
    
    const POST = "POST";
    const loginUrl = "https://localhost:8083/login/";

    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400};

    let loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Login Form submission stopped.");

        var n = event.srcElement.length;
        for(var i = 0; i < n; i++) {
            console.log(event.srcElement[i].value);
        }

        submitLoginForm();

    });

    function submitLoginForm() {
        
        let loginParams = {
            method: POST,
            body: new FormData(loginForm),
            redirect: "follow"
        };

        fetch(loginUrl, loginParams)
            .then(response => checkStatus(response))
            .catch(err => {
                console.log("Caught error: " + err);
            });
    }

    function checkStatus(response) {
        let status = response.status;

        if(status === HTTP_STATUS.OK) {
            window.location.href = "/packages/";
        } else if(status === HTTP_STATUS.BAD_REQUEST) {
            displayAlert();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayAlert() {
        let alertDiv = document.getElementById("alert-div");
        alertDiv.innerHTML = "";
        let text = document.createTextNode("Niepoprawne dane.")
        alertDiv.setAttribute("class", "alert alert-danger");
        alertDiv.setAttribute("role", "alert");
        alertDiv.appendChild(text);
                 
    }

});