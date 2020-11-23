document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";
    const URL = "https://localhost:8080/";

    const LOGIN_FIELD_ID = "login";
    const PESEL_FIELD_ID = "pesel";
    const PASSWORD_FIELD_ID = "password";
    const SECOND_PASSWORD_FIELD_ID = "second_password";
    const BUTTON_ID = "button-registration-form";
    const NAME_FIELD_ID = "name";
    const SURNAME_FIELD_ID = "surname";
    const BIRTHDAY_FIELD_ID = "date_of_birth";
    const STREET_FIELD_ID = "street";
    const NUMBER_FIELD_ID = "number";
    const POSTAL_CODE_FIELD_ID = "postal_code";
    const CITY_FIELD_ID = "city";
    const COUNTRY_FIELD_ID ="country";


    var HTTP_STATUS = {OK: 200, CREATED: 201, NOT_FOUND: 404};
    var registerAlertId = "registerMessage";
    var registerMessage = "Zarejestrowano!";
    var loginBeforeRegistration = false;

    prepareEventOnLoginChange();

    let registrationForm = document.getElementById("registration-form");

    registrationForm.addEventListener("submit", function (event) {
        event.preventDefault();
        console.log("Form submission stopped.");
        updateLoginAvailabilityMessage();

        var n = event.srcElement.length;
        for (var i = 0; i < n; i++){
            console.log(event.srcElement[i].value);
        }
        
        var c1 = isLoginCorrect();
        var c2 = isPeselCorrect();
        var c3 = isPasswordCorrect();
        var c4 = isSecondPasswordCorrect();
        var c5 = isElementStringCorrect(NAME_FIELD_ID, "nameWarning");
        var c6 = isElementStringCorrect(SURNAME_FIELD_ID, "surnameWarning");
        var c7 = isElementStringCorrect(CITY_FIELD_ID, "cityWarning");
        var c8 = isElementStringCorrect(COUNTRY_FIELD_ID, "countryWarning");
        var c9 = isElementLengthCorrect(BIRTHDAY_FIELD_ID, "birthdayWarning");
        var c10 = isElementLengthCorrect(STREET_FIELD_ID, "streetWarning");
        var c11 = isElementLengthCorrect(NUMBER_FIELD_ID, "numberWarning");
        var c12 = isElementLengthCorrect(POSTAL_CODE_FIELD_ID, "postalCodeWarning");

        if (c1 == true && c2 == true && c3 == true && c4 == true && c5 == true && c6 == true
            && c7 ==true && c8 == true && c9 ==true && c10 == true && c11 == true
            && c12 == true && loginBeforeRegistration == true) {
            submitRegisterForm();
        } else {
            removeWarningMessage(registerAlertId);
            console.log("Wrong data");
        }
    });

    function submitRegisterForm() {
        let registerUrl = URL + "register";

        let registerParams = {
            method: POST,
            body: new FormData(registrationForm),
            redirect: "follow"
        };

        fetch(registerUrl, registerParams)
                .then(response => getRegisterResponseData(response))
                .then(response => displayInConsoleCorrectResponse(response))
                .catch(err => {
                    console.log("Caught error: " + err);
                });
    }

    function getRegisterResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.CREATED) {
            showWarningMessage(registerAlertId, registerMessage, BUTTON_ID);
            return response.json();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexpected response status: " + response.status;
        }
    }

    function displayInConsoleCorrectResponse(correctResponse) {
        let status = correctResponse.registration_status;

        console.log("Status: " + status);

        if (status !== "OK") {
            removeWarningMessage(registerAlertId);
            console.log("Errors: " + correctResponse.errors);
        }
    }

    function prepareEventOnLoginChange() {
        let loginInput = document.getElementById(LOGIN_FIELD_ID);
        loginInput.addEventListener("change", updateLoginAvailabilityMessage);
    }

    function updateLoginAvailabilityMessage() {
        let warningElemId = "loginWarning";
        let warningMessage = "Login jest zajęty.";

        isLoginAvailable().then(function (isAvailable) {
            if (isAvailable) {
                console.log("Available login!");
                removeWarningMessage(warningElemId);
            } else {
                console.log("NOT available login");
                showWarningMessage(warningElemId, warningMessage, LOGIN_FIELD_ID);
            }
        }).catch(function (error) {
            console.error("Something went wrong while checking login.");
            console.error(error);
        });
    }

    function showWarningMessage(newElemId, message, parentElem) {
        let warningElem = prepareWarningElem(newElemId, message);
        appendAfterElem(parentElem, warningElem);
    }

    function removeWarningMessage(warningElemId) {
        let warningElem = document.getElementById(warningElemId);

        if (warningElem !== null) {
            warningElem.remove();
        }
    }

    function prepareWarningElem(newElemId, message) {
        let warningField = document.getElementById(newElemId);

        if (warningField === null) {
            let textMessage = document.createTextNode(message);
            warningField = document.createElement('span');

            warningField.setAttribute("id", newElemId);
            warningField.className = "warning-field";
            warningField.appendChild(textMessage);
        }
        return warningField;
    }

    function appendAfterElem(currentElemId, newElem) {
        let currentElem = document.getElementById(currentElemId);
        currentElem.insertAdjacentElement('afterend', newElem);
    }

    function isLoginAvailable() {
        return Promise.resolve(checkLoginAvailability().then(function (statusCode) {
            console.log(statusCode);
            if (statusCode === HTTP_STATUS.OK) {
                loginBeforeRegistration = false;
                return false;

            } else if (statusCode === HTTP_STATUS.NOT_FOUND) {
                loginBeforeRegistration = true;
                return true;

            } else {
                throw "Unknown login availability status: " + statusCode;
            }
        }));
    }

    function checkLoginAvailability() {
        let loginInput = document.getElementById(LOGIN_FIELD_ID);
        let baseUrl = URL + "user/";
        let userUrl = baseUrl + loginInput.value;

        return Promise.resolve(fetch(userUrl, {method: GET}).then(function (resp) {
            return resp.status;
        }).catch(function (err) {
            return err.status;
        }));
    }

    function isLoginCorrect() {
        let login = document.getElementById(LOGIN_FIELD_ID);    
        let warningElemId = "loginWarning";
        let warningMessage1 = "Login musi składać się z min. 5 znaków.";
        let warningMessage2 = "Login musi zawierać tylko litery.";
        var letters = /^[A-Za-z]+$/;

        if (login.value.length < 5) {
            showWarningMessage(warningElemId, warningMessage1, LOGIN_FIELD_ID);
            return false;
        } else {
            removeWarningMessage(warningElemId);
        }

        if (login.value.match(letters)) {
            removeWarningMessage(warningElemId);            
        } else {
            showWarningMessage(warningElemId, warningMessage2, LOGIN_FIELD_ID);
            return false;
        }

        return true;
    }

    function isPeselCorrect() {
        var numbers = /^[0-9]+$/;
        let pesel = document.getElementById(PESEL_FIELD_ID);
        let warningElemId = "peselWarning";
        let warningMessage = "Niepoprawny PESEL.";

        if (pesel.value.length == 11 && pesel.value.match(numbers))  {
            var p = pesel.value;
            var sum = parseInt(p.charAt(0)) * 1 + parseInt(p.charAt(1)) * 3 + parseInt(p.charAt(2)) * 7 + parseInt(p.charAt(3)) * 9 + parseInt(p.charAt(4)) * 1
                + parseInt(p.charAt(5)) * 3 + parseInt(p.charAt(6)) * 7 + parseInt(p.charAt(7)) * 9 + parseInt(p.charAt(8)) * 1 + parseInt(p.charAt(9)) * 3;
            var lastDigit = sum % 10;
            if (10 - lastDigit == parseInt(p.charAt(10))) {
                removeWarningMessage(warningElemId);
            } else {
                showWarningMessage(warningElemId, warningMessage, PESEL_FIELD_ID);
                return false;
            }
        } else {
            showWarningMessage(warningElemId, warningMessage, PESEL_FIELD_ID);
            return false;
        }
        return true;
    }

    function isPasswordCorrect() {
        let password = document.getElementById(PASSWORD_FIELD_ID);
        let warningElemId = "passwordWarning";
        let warningMessage1 = "Hasło musi zawierać minimum 8 znaków.";
        let warningMessage2 = "Hasło musi zawierać dużą i małą literę, cyfrę oraz znak specjalny.";

        if (password.value.length < 8) {
            showWarningMessage(warningElemId, warningMessage1, PASSWORD_FIELD_ID);
            return false;
        } else {
            removeWarningMessage(warningElemId);
        }

        if (password.value.match(/[a-z]+/) && password.value.match(/[A-Z]+/) 
            && password.value.match(/[0-9]+/) && password.value.match(/[!@#$%^&*]+/)) {
            removeWarningMessage(warningElemId);
        } else {
            showWarningMessage(warningElemId, warningMessage2, PASSWORD_FIELD_ID);
            return false;
        }

        return true;
    }

    function isSecondPasswordCorrect() {
        let password = document.getElementById(PASSWORD_FIELD_ID);
        let second_password = document.getElementById(SECOND_PASSWORD_FIELD_ID);
        let warningElemId = "secondPasswordWarning";
        let warningMessage = "Hasła są różne.";

        if(password.value == second_password.value) {
            removeWarningMessage(warningElemId);
            return true;
        } else {
            showWarningMessage(warningElemId, warningMessage, SECOND_PASSWORD_FIELD_ID);
            return false;
        }
    }

    function isElementStringCorrect(element, warningElemId) {
        let field = document.getElementById(element);
        let warningMessage = "Pole może zawierać tylko litery.";
        var letters = /^[A-Za-z]+$/;

        if (field.value.length < 1 || field.value.match(letters) == false) {
            showWarningMessage(warningElemId, warningMessage, element);
            return false;
        } else {
            removeWarningMessage(warningElemId);
            return true;
        }

    }

    function isElementLengthCorrect(element ,warningElemId) {
        let field = document.getElementById(element);
        let warningMessage = "Pole nie może być puste.";

        if (field.value.replace(/\s/g, '').length < 1) {
            showWarningMessage(warningElemId, warningMessage, element);
            return false;
        } else {
            removeWarningMessage(warningElemId);
            return true;
        }
    }

});