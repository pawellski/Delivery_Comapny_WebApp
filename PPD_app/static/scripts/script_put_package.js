document.addEventListener('DOMContentLoaded', function (event) {

    var packageURL = "https://localhost:8082/package/";
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, CONFLICT: 409};
    var POST = "POST";

    var putPackageForm = document.getElementById("put-package");

    putPackageForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Put Package Form Submission stopped.");

        submitPutPackage();
    });

    function submitPutPackage() {
        let packageParams = {
            method: POST,
            body: new FormData(putPackageForm),
            redirect: "follow"
        }

        fetch(packageURL,packageParams)
            .then(response => getPutPackageResponseData(response))
            .then(response => displayAlert(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });
    }

    function getPutPackageResponseData(response){
        let status = response.status;

        if(status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST || HTTP_STATUS.CONFLICT) {
            return response.status
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayAlert(status) {
        let alertDiv = document.getElementById("alert-div");
        alertDiv.innerHTML = ""
        if (status == 200) {
            let text = document.createTextNode("Proces umieszczania paczki w paczkomacie przebiegł pomyślnie.")
            alertDiv.setAttribute("class", "alert alert-success");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else if (status == 400) {
            let text = document.createTextNode("Dane zostały wprowadzone niepoprawnie. Spróbuj ponownie.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else {
            let text = document.createTextNode("Paczka została już umieszczona w paczkomacie.")
            alertDiv.setAttribute("class", "alert alert-warning");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        }

    }

});