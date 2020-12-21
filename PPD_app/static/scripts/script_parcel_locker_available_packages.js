document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, UNAUTHORIZED: 401};
    
    var packages0URL = "https://localhost:8082/packages/list/0";
    var pickupURL = "https://localhost:8082/pickup_package/"
    var GET = "GET";
    var POST = "POST";
    var currentParcelLocker = window.localStorage.getItem("currentParcelLocker");
    console.log(currentParcelLocker);

    let packagesToRecive = [];

    getPackagesList(packages0URL);

    function getPackagesList(URL) {
        let correctURL = URL + "?PL=" + currentParcelLocker;
        token = "Bearer " + window.localStorage.getItem("access_token");
        let params = {
            method: GET,
            headers: {'Authorization': token},
            redirect: "follow"
        };

        fetch(correctURL, params)
            .then(response => getResponseData(response))
            .then(response => displayTableWithPackages(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });

    }

    function getResponseData(response) {
        let status = response.status;

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json()
        } else if (status == HTTP_STATUS.UNAUTHORIZED) {
            window.location.href = "/courier_page/";
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayTableWithPackages(response) {
        response = JSON.parse(response);
        console.log(response)
        let availablePackagesElem = document.getElementById("available-packages");
        let numberOfPackages = response.numberOfPackages;

        availablePackagesElem.innerHTML = "";
        let title = document.createElement("h2");
        title.setAttribute("class", "text-center");
        let msg = "PACZKOMAT " + window.localStorage.getItem("currentParcelLocker");
        let titleText = document.createTextNode(msg);
        title.appendChild(titleText);
        availablePackagesElem.appendChild(title);

        if(numberOfPackages != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("class", "table table-striped")
            tableElem.setAttribute("id", "available-packages-table");
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let trHead = document.createElement("tr");
            let th1 = document.createElement("th");
            th1.setAttribute("scope", "col");
            th1Text = document.createTextNode("Numer paczki");
            th1.appendChild(th1Text);
            let th2 = document.createElement("th");
            th2.setAttribute("scope", "col");
            th2Text = document.createTextNode(" ");
            th2.appendChild(th2Text);
            trHead.appendChild(th1);
            trHead.appendChild(th2);
            tableHeadElem.appendChild(trHead);
            
            for (var i = 0; i < response.packages.length; i++) {
                let row = document.createElement("tr");
                let cell1 = document.createElement("td");
                let text1 = document.createTextNode(response.packages[i].id);
                cell1.appendChild(text1);
                row.appendChild(cell1);
                let cell2 = document.createElement("td");
                let checkBox = document.createElement("input");
                checkBox.setAttribute("class", "form-check-input");
                checkBox.setAttribute("type", "checkbox");
                checkBox.setAttribute("value", "");
                if (packagesToRecive.includes(response.packages[i].id)) {
                    checkBox.checked = true;
                }
                checkBox.addEventListener("click", function(event) {
                    let id = event.currentTarget.parentNode.parentNode.children[0].textContent;
                    if(checkBox.checked == true){
                        packagesToRecive.push(id)
                    } else {
                        if(packagesToRecive.includes(id)) {
                            let index = packagesToRecive.indexOf(id);
                            packagesToRecive.splice(index, 1)
                        }
                    }
                    console.log(packagesToRecive)
                })
                cell2.appendChild(checkBox);
                row.appendChild(cell2);
                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableHeadElem);
            tableElem.appendChild(tableBodyElem);
            availablePackagesElem.appendChild(tableElem);

            let paginationUl = document.createElement("ul");
            paginationUl.setAttribute("class", "pagination justify-content-center");
            
            let liPrev = document.createElement("li");
            liPrev.setAttribute("id", "liPrev");
            liPrev.setAttribute("class", "page-item");
            let aPrev = document.createElement("a");
            aPrev.setAttribute("class", "page-link");
            aPrev.addEventListener("click", function(event) {
                getPackagesList(response.previous)
            });
            let textPrev = document.createTextNode("<");
            aPrev.appendChild(textPrev);
            liPrev.appendChild(aPrev);
            paginationUl.appendChild(liPrev);
            
            let liNext = document.createElement("li");
            liNext.setAttribute("id", "liNext");
            liNext.setAttribute("class", "page-item");
            let aNext = document.createElement("a");
            aNext.setAttribute("class", "page-link");
            aNext.addEventListener("click", function(event) {
                getPackagesList(response.next)
            });
            let textNext = document.createTextNode(">");
            aNext.appendChild(textNext);
            liNext.appendChild(aNext);
            paginationUl.appendChild(liNext);

            availablePackagesElem.appendChild(paginationUl);

        } else {
            let lackOfPackagesElem = document.createElement('h3');
            let lackOfPackagesContent = document.createTextNode("Aktulnie w paczkomacie nie ma nadanych paczek.");
            lackOfPackagesElem.setAttribute("class", "text-center h3-head");
            lackOfPackagesElem.setAttribute("id", "lackOfPackages");
            lackOfPackagesElem.appendChild(lackOfPackagesContent);
            availablePackagesElem.appendChild(lackOfPackagesElem);
        }
        let closeButton = document.createElement("button");
        let buttonText = document.createTextNode("Zapisz zmiany");
        closeButton.setAttribute("class", "btn btn-lg btn-secondary btn-block");
        closeButton.appendChild(buttonText);
        closeButton.addEventListener("click", function(event) {
            packagesToRecive.forEach(function(item) {
                submitSavedChanges(item);
            });
            window.location.href = "/courier_page/";
        });

        availablePackagesElem.appendChild(closeButton);       
    }

    function submitSavedChanges (package_id) {
        let parcel_locker_id = window.localStorage.getItem("currentParcelLocker");
        let formData = new FormData();
        formData.append("package_id", package_id)
        formData.append("parcel_locker_id", parcel_locker_id)
        token = "Bearer " + window.localStorage.getItem("access_token");
        let params = {
            method: POST,
            headers: {'Authorization': token},
            body: formData,
            redirect: "follow"
        };

        fetch(pickupURL, params)
            .then(response => getPickupPackageResponse(response))
            .catch(err => {
                console.log("Caught error: " + err);
            });

    }

    function getPickupPackageResponse(response) {
        let status = response.status

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            console.log(status)
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }
});
