document.addEventListener('DOMContentLoaded', function (event) {

    var pickupPackageURL = "https://localhost:8083/pickup_package/";
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, CONFLICT: 409};
    var POST = "POST";

    var passOnPackageForm = document.getElementById("passon-package-form");

    passOnPackageForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Pass On Package Form Submission stopped.");

        submitPassOnPackage();
    });

    function submitPassOnPackage() {
        let packageParams = {
            method: POST,
            body: new FormData(passOnPackageForm),
            redirect: "follow"
        }

        fetch(pickupPackageURL, packageParams)
            .then(response => getPassOnPackageResponseData(response))
            .then(response => displayAlert(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });

    }

    function getPassOnPackageResponseData(response) {
        let status = response.status;

        if(status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST || HTTP_STATUS.CONFLICT) {
            return response.status
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayAlert(status) {
        let alertDiv = document.getElementById("alert-div-2");
        alertDiv.innerHTML = ""
        if (status == 200) {
            let text = document.createTextNode("Proces przekazania paczki przebiegł pomyślnie.")
            alertDiv.setAttribute("class", "alert alert-success");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else if (status == 400) {
            let text = document.createTextNode("Paczka o podanym numerze nie istnieje.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else {
            let text = document.createTextNode("Paczka nie może zostać przekazana, ponieważ proces jej dostawy jest w toku.")
            alertDiv.setAttribute("class", "alert alert-warning");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        }

    }

});