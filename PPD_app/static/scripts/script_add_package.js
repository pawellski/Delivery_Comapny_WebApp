document.addEventListener('DOMContentLoaded', function (event) {
    
    var tokenURL = "https://localhost:8080/token/";
    var packageURL = "https://localhost:8081/add_package/";
    
    var GET = "GET";
    var POST = "POST";

    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400};
    let addPackageForm = document.getElementById("add-package-form");

    var SENDER_NAME_ID = "sender_name";
    var SENDER_SURNAME_ID = "sender_surname";
    var SENDER_STREET_ID = "sender_street";
    var SENDER_NUMBER_ID = "sender_number";
    var SENDER_POSTAL_CODE_ID = "sender_postal_code";
    var SENDER_CITY_ID = "sender_city";
    var SENDER_COUNTRY_ID = "sender_country";
    var SENDER_PHONE_NUMBER_ID = "sender_phone_number";
    var RECIPIENT_NAME_ID = "recipient_name";
    var RECIPIENT_SURNAME_ID = "recipient_surname";
    var RECIPIENT_STREET_ID = "recipient_street";
    var RECIPIENT_NUMBER_ID = "recipient_number";
    var RECIPIENT_POSTAL_CODE_ID = "recipient_postal_code";
    var RECIPIENT_CITY_ID = "recipient_city";
    var RECIPIENT_COUNTRY_ID = "recipient_country";
    var RECIPIENT_PHONE_NUMBER_ID = "recipient_phone_number";
    var BUTTON_ID = "button-add-package-form";

    get_token();

    addPackageForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Add Package Form submission stopped.");

        var n = event.srcElement.length;
        for(var i = 0; i < n; i++) {
            console.log(event.srcElement[i].value);
        }

        errors = 0;
        errors = isElementLengthCorrect(SENDER_NAME_ID, errors);
        errors = isElementLengthCorrect(SENDER_SURNAME_ID, errors);
        errors = isElementLengthCorrect(SENDER_STREET_ID, errors);
        errors = isElementLengthCorrect(SENDER_NUMBER_ID,errors);
        errors = isElementLengthCorrect(SENDER_POSTAL_CODE_ID, errors);
        errors = isElementLengthCorrect(SENDER_CITY_ID, errors);
        errors = isElementLengthCorrect(SENDER_COUNTRY_ID, errors);
        errors = isElementLengthCorrect(SENDER_PHONE_NUMBER_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_NAME_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_SURNAME_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_STREET_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_NUMBER_ID,errors);
        errors = isElementLengthCorrect(RECIPIENT_POSTAL_CODE_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_CITY_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_COUNTRY_ID, errors);
        errors = isElementLengthCorrect(RECIPIENT_PHONE_NUMBER_ID, errors);

        if (errors == 0) {
            submitAddPackage();
        } else {
            showWarning();
        }
    });

    function submitAddPackage() {
        token = "Bearer " + window.localStorage.getItem("access_token");
        let packageParams = {
            method: POST,
            headers: {'Authorization': token},
            body: new FormData(addPackageForm),
            redirect: "follow"
        }

        fetch(packageURL,packageParams)
            .then(response => getAddPackageResponseData(response))
            .then(response => displayInConsoleInformation(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });

    }

    function getAddPackageResponseData(response) {
        let status = response.status;

        if(status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json();
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayInConsoleInformation(correctResponse) {
        let status = correctResponse.add_package;
        console.log("Status: " + status);

        if(status == "Correct") {
            showInformation();            
        } else {
            showWarning();
        }
    }

    function showInformation() {
        removeMessages();
        let informationElement = document.getElementById("informationMessage");
        let informationMessage = document.createTextNode("Dodano paczkę do systemu!");
        let currentElem = document.getElementById(BUTTON_ID);
        informationElement = document.createElement('span');
        informationElement.setAttribute("id", "informationMessage");
        informationElement.appendChild(informationMessage);
        currentElem.insertAdjacentElement('afterend', informationElement);
    }

    function showWarning () {
        removeMessages();
        let warningElement = document.getElementById("warningMessage");
        let warningMessage = document.createTextNode("Pola nie mogą być puste!");
        let currentElem = document.getElementById(BUTTON_ID);
        warningElement = document.createElement('span');
        warningElement.setAttribute("id", "warningMessage");
        warningElement.className = "warning-field";
        warningElement.appendChild(warningMessage);
        currentElem.insertAdjacentElement('afterend', warningElement);        
    }

    function removeMessages() {
        let informationMessage = document.getElementById("informationMessage");
        let warningMessage = document.getElementById("warningMessage");

        if (informationMessage !== null) {
            informationMessage.remove();
        }

        if (warningMessage !== null) {
            warningMessage.remove();
        }
    }

    function isElementLengthCorrect(element, errors) {
        let field = document.getElementById(element);

        if (field.value.replace(/\s/g, '').length < 1) {
            errors = errors + 1;
            return errors;
        } else {
            return errors;
        }
    }
    
    
    
    function get_token() {
        let params = {
            method: GET,
            redirect: "follow"
        }
        
        fetch(tokenURL, params)
            .then(response => getResponseData(response))
            .then(response => setToken(response))
            .catch(err => {
                console.log("Caught error:" + err);
            });         

    }

    function getResponseData(response) {
        let status = response.status;

        if (status = HTTP_STATUS.OK) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function setToken(correctResponse) {
        window.localStorage.setItem("access_token", correctResponse.access_token);
        console.log("Set token correctly!")
    }



});