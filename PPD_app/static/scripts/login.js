document.addEventListener('DOMContentLoaded', function (event) {

    const POST = "POST"
    const loginUrl = "https://localhost:8080/login"

    const BUTTON_ID = "button-login-form";

    var HTTP_STATUS = {OK: 200, NOT_FOUND: 404};

    let loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("LoginFrom submission stopped.");

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
            .catch(err => {
                console.log("Caught error: " + err);
            });
    }

    function getLoginResponseData(response) {
        let status = response.status;

        if(status == HTTP_STATUS.OK || HTTP_STATUS.NOT_FOUND) {
            if(status == HTTP_STATUS.OK ) {
                console.log("Logged in correctly.")
            } else {
                console.log("Wrong login or password.")
            }
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }




});