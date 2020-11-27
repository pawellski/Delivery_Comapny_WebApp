document.addEventListener('DOMContentLoaded', function (event) {

    const POST = "POST"
    const loginUrl = "https://localhost:8080/login"

    const BUTTON_ID = "button-login-form";

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
            .then(response => getLoginResponseData(response))
            .then(response => displayInConsoleCorrectResponse(response))
            .catch(err => {
                console.log("Caught error: " + err);
            });
    }

    function getLoginResponseData(response) {
        let status = response.status;

        if(status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayInConsoleCorrectResponse(correctResponse) {
        let status = correctResponse.login;
        console.log("Status: " + status)

        if(status == "Ok") {
            window.localStorage.setItem("access_token", correctResponse.access_token);
            window.location.href = "/user_homepage";
        } else {
            showWarningMessage();
        }
    }
    
    function showWarningMessage() {
        let warningField = document.getElementById("loginWarning");
        let currentElem = document.getElementById(BUTTON_ID);

        if(warningField === null) {
            let textMessage = document.createTextNode("Niepoprawne dane!");
            warningField = document.createElement('span');
            warningField.setAttribute("id", "loginWarning");
            warningField.className = "warning-field";
            warningField.appendChild(textMessage);
            currentElem.insertAdjacentElement('afterend', warningField)
        }
        
    }




});