document.addEventListener('DOMContentLoaded', function (event) {

    var authorizationURL = "https://localhost:8082/courier_page/";
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, UNAUTHORIZED: 401};
    var POST = "POST";

    var authorizationForm = document.getElementById("authorization-form");

    authorizationForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Authorization Form Submission stopped.");
        window.localStorage.setItem("currentParcelLocker", event.srcElement[0].value)

        submitAUthorizationForm();
    });

    function submitAUthorizationForm() {
        let authorizationParams = {
            method: POST,
            body: new FormData(authorizationForm),
            redirect: "follow"
        };

        fetch(authorizationURL, authorizationParams)
            .then(response => getAuthorizationResponse(response))
            .then(response => displayInformation(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });
    }

    function getAuthorizationResponse(response) {
        let status = response.status;

        if(status == HTTP_STATUS.OK || status == HTTP_STATUS.BAD_REQUEST || status == HTTP_STATUS.UNAUTHORIZED) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayInformation(responseData) {
        let authorization = responseData.Authorization;

        if(authorization == "Correct") {
            window.localStorage.setItem("access_token", responseData.access_token);
            window.location.href = "/available_packages/";
        } else if(authorization == "Unauthorized"){
            let alertDiv = document.getElementById("alert-div");
            alertDiv.innerHTML = ""
            let text = document.createTextNode("Nie jesteśmy w stanie potwierdzić Twojej tożsamości.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);

        } else {
            let alertDiv = document.getElementById("alert-div");
            alertDiv.innerHTML = ""
            let text = document.createTextNode("Paczkomat o podanym identyfikatorze nie istnieje.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        }
    }


    

});