document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200};
    var tokenURL = "https://localhost:8080/get_token";
    var packagesURL = "https://localhost:8081/get_packages";
    var GET = "GET";

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
            let column1 = document.createTextNode("Identyfikator Paczki");
            let column2 = document.createTextNode("Data Utworzenia Paczki");
            let column3 = document.createTextNode("Pobierz Plik PDF");
            td1.appendChild(column1);
            td2.appendChild(column2);
            td3.appendChild(column3);
            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);
            tableHeadElem.appendChild(tr);
            tableElem.appendChild(tableHeadElem);

            for (var i = 0; i < numberOfPackages; i++) {
                var row = document.createElement("tr");
                var cell1 = document.createElement("td");
                var text1 = document.createTextNode(Object.keys(response)[i]);
                cell1.appendChild(text1);
                row.appendChild(cell1);
                var cell2 = document.createElement("td");
                var text2 = document.createTextNode(Object.values(response)[i]);
                cell2.appendChild(text2);
                row.appendChild(cell2);
                var cell3 = document.createElement("td");
                var text3 = document.createTextNode("Pobierz");
                var aElem = document.createElement("a");
                var token = window.localStorage.getItem("access_token");
                var link = downloadURL + "/" + Object.keys(response)[i] + "?token=" + token;
                aElem.setAttribute("href", link);
                aElem.appendChild(text3);
                cell3.appendChild(aElem);
                row.appendChild(cell3);
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