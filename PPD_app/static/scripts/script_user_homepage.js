document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200};
    var tokenURL = "https://localhost:8080/token/";
    var packagesURL = "https://localhost:8081/packages/";
    var downloadURL = "https://localhost:8081/waybill/";
    var removeURL = "https://localhost:8081/remove_package/"
    var GET = "GET";
    var DELETE = "DELETE";

    getToken();
    getPackgaesList();

    function getPackgaesList () {
        token = "Bearer " + window.localStorage.getItem("access_token");
        let params = {
            method: GET,
            headers: {'Authorization': token},
            redirect: "follow"
        }

        fetch(packagesURL, params)
            .then(response => getResponseData(response))
            .then(response => displayTableWithPackages(response))
            .catch(err => {
                console.log("Caught error:" + err);
            });
    }

    function displayTableWithPackages(response) {
        response = JSON.parse(response)
        let myPackagesElem = document.getElementById("my-packages");
        let summaryElem = document.getElementById("summary");
        numberOfPackages = Object.keys(response).length;

        if (numberOfPackages != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("id", "user-packages-table")
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let tr = document.createElement("tr");
            let td1 = document.createElement("td");
            let td2 = document.createElement("td");
            let td3 = document.createElement("td");
            let td4 = document.createElement("td");
            let td5 = document.createElement("td");
            let column1 = document.createTextNode("Identyfikator Paczki");
            let column2 = document.createTextNode("Data Utworzenia Paczki");
            let column3 = document.createTextNode("Status");
            let column4 = document.createTextNode("Pobierz PDF");
            let column5 = document.createTextNode("Usuń paczkę");
            td1.appendChild(column1);
            td2.appendChild(column2);
            td3.appendChild(column3);
            td4.appendChild(column4);
            td5.appendChild(column5);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tr.appendChild(td4);
            tr.appendChild(td5);
            tableHeadElem.appendChild(tr);
            tableElem.appendChild(tableHeadElem);

            for (var i = 0; i < numberOfPackages; i++) {
                var row = document.createElement("tr");
                var cell1 = document.createElement("td");
                var text1 = document.createTextNode(response[i].id);
                cell1.appendChild(text1);
                row.appendChild(cell1);
                var cell2 = document.createElement("td");
                var text2 = document.createTextNode(response[i].date);
                cell2.appendChild(text2);
                row.appendChild(cell2);
                var cell3 = document.createElement("td");
                var text3 = document.createTextNode(response[i].status);
                cell3.appendChild(text3);
                row.appendChild(cell3);
                var cell4 = document.createElement("td");
                var text4 = document.createTextNode("Pobierz");
                var aElem = document.createElement("a");
                var token = window.localStorage.getItem("access_token");
                var link = downloadURL + response[i].id + "?token=" + token;
                aElem.setAttribute("href", link);
                aElem.appendChild(text4);
                cell4.appendChild(aElem);
                row.appendChild(cell4);
                if(response[i].status === "Nowa") {
                    console.log(response[i].id)
                    var cell5 = document.createElement("td");
                    var text5 = document.createTextNode("Usuń");
                    var button = document.createElement("button");
                    button.setAttribute("class", "remove-button")
                    button.appendChild(text5);
                    button.addEventListener("click", function(e) {
                        let token = "Bearer " + window.localStorage.getItem("access_token");
                        id = button.parentElement.parentElement.children[0].textContent;
                        let removePackageURL = removeURL + id;
                        let removePackageParams = {
                            method: DELETE,
                            headers: {'Authorization': token},
                            redirect: "follow"
                        }

                        fetch(removePackageURL, removePackageParams)
                            .then(response => getDeleteStatus(response))
                            .catch(err => {
                                console.log("Caught error: " + err);
                            })
                        
                        location.reload();
                    });
                    cell5.appendChild(button);
                    row.appendChild(cell5);
                } else {
                    var cell5 = document.createElement("td");
                    row.appendChild(cell5);
                }
                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableBodyElem);
            myPackagesElem.appendChild(tableElem);
            

        } else {
            let lackOfPackagesElem = document.createElement('h3');
            let lackOfPackagesContent = document.createTextNode("Brak nadanych paczek!");
            lackOfPackagesElem.setAttribute("id", "lackOfPackages");
            lackOfPackagesElem.appendChild(lackOfPackagesContent);
            myPackagesElem.appendChild(lackOfPackagesElem);

            let moreInformationElem = document.createElement('p');
            let moreInformationContent = document.createTextNode("Nie posiadasz jeszcze nadanych paczek.\
                W celu nadania swojej pierwszej paczki, przejdź do sekcji \"NADAJ PACZKĘ\". Powodzenia! ");
            moreInformationElem.setAttribute("id", "lackOfPackages");
            moreInformationElem.appendChild(moreInformationContent);
            myPackagesElem.appendChild(moreInformationElem);

        }
        
        console.log(numberOfPackages)
        let numberOfPackagesElem = document.getElementById("numberOfPackages");
        let numberOfPackagesContent = document.createTextNode("Liczba wysłanych paczek: " + numberOfPackages);
        numberOfPackagesElem = document.createElement('h3');
        numberOfPackagesElem.setAttribute("id", "numberOfPackages");
        numberOfPackagesElem.appendChild(numberOfPackagesContent);
        summaryElem.appendChild(numberOfPackagesElem);

    }

    function getDeleteStatus(response) {
        let status = response.status;
        console.log(status);
    }

    function getToken() {
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