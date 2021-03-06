document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400};
    var tokenURL = "https://localhost:8080/token/";
    var packages0URL = "https://localhost:8081/packages/list/0";
    var packageURL = "https://localhost:8081/package/"
    var GET = "GET";
    var DELETE = "DELETE";

    const PUT_PACKAGE_ROOM = "put-package-room";
    const PICKUP_PACKAGE_ROOM = "pickup-package-room";
    const PASSON_PACKAGE_ROOM = "passon-package-room";

    let currentPackagesURL = packages0URL;

    getToken();

    var ws_uri = "https://localhost:8084";
    socket = io.connect(ws_uri);
    joinIntoRoom(PUT_PACKAGE_ROOM);
    joinIntoRoom(PICKUP_PACKAGE_ROOM);
    joinIntoRoom(PASSON_PACKAGE_ROOM);

    socket.on("connect", function () {
        console.log("Correctly connected to the chat");
    });

    socket.on("joined_room", function (message) {
        console.log("Joined to the room ", message);
    });

    socket.on("chat_message", function (data) {
        getPackgaesList(currentPackagesURL);
        console.log("Received new chat message:", data);

    });

    function joinIntoRoom(room_id) {
        socket.emit("join", {room_id: room_id });
    }

    function getPackgaesList (URL) {
        currentPackagesURL = URL;

        token = "Bearer " + window.localStorage.getItem("access_token");
        let params = {
            method: GET,
            headers: {'Authorization': token},
            redirect: "follow"
        }

        fetch(URL, params)
            .then(response => getResponseData(response))
            .then(response => displayTableWithPackages(response))
            .catch(err => {
                console.log("Caught error:" + err);
            });
    }

    function displayTableWithPackages(response) {
            response = JSON.parse(response);
            let myPackagesElem = document.getElementById("my-packages");
            let summaryElem = document.getElementById("summary");
            numberOfPackages = response.numberOfPackages;

            if (numberOfPackages != 0) {
                document.getElementById("my-packages").innerHTML = "";
                document.getElementById("summary").innerHTML = "";
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

                for (var i = 0; i < response.packages.length; i++) {
                    var row = document.createElement("tr");
                    var cell1 = document.createElement("td");
                    var text1 = document.createTextNode(response.packages[i].id);
                    cell1.appendChild(text1);
                    row.appendChild(cell1);
                    var cell2 = document.createElement("td");
                    var text2 = document.createTextNode(response.packages[i].date);
                    cell2.appendChild(text2);
                    row.appendChild(cell2);
                    var cell3 = document.createElement("td");
                    var text3 = document.createTextNode(response.packages[i].status);
                    cell3.appendChild(text3);
                    row.appendChild(cell3);
                    var cell4 = document.createElement("td");
                    var text4 = document.createTextNode("Pobierz");
                    var aElem = document.createElement("a");
                    var token = window.localStorage.getItem("access_token");
                    var link = packageURL + response.packages[i].id + "?token=" + token;
                    aElem.setAttribute("href", link);
                    aElem.appendChild(text4);
                    cell4.appendChild(aElem);
                    row.appendChild(cell4);
                    if(response.packages[i].status === "Nowa") {
                        var cell5 = document.createElement("td");
                        var text5 = document.createTextNode("Usuń");
                        var removeButton = document.createElement("button");
                        removeButton.setAttribute("class", "remove-button");
                        removeButton.appendChild(text5);

                        removeButton.addEventListener("click", function(e) {
                            var id = e.currentTarget.parentNode.parentNode.children[0].textContent
                            let token = "Bearer " + window.localStorage.getItem("access_token");
                            let removePackageURL = packageURL + id;
                            
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

                        cell5.appendChild(removeButton);
                        row.appendChild(cell5);
                    } else {
                        var cell5 = document.createElement("td");
                        row.appendChild(cell5);
                    }
                    tableBodyElem.appendChild(row);
                }

                tableElem.appendChild(tableBodyElem);
                myPackagesElem.appendChild(tableElem);
                
                var prevText = document.createTextNode("<");
                var buttonPrev = document.createElement("button");
                buttonPrev.setAttribute("id", "prev-button");
                buttonPrev.appendChild(prevText);
                myPackagesElem.appendChild(buttonPrev);
                buttonPrev.addEventListener("click", function(e) {
                    var prevURL = response.previous;
                    getPackgaesList(prevURL);
                })

                var nextText = document.createTextNode(">");
                var buttonNext = document.createElement("button");
                buttonNext.setAttribute("id", "next-button");
                buttonNext.appendChild(nextText);
                myPackagesElem.appendChild(buttonNext);
                buttonNext.addEventListener("click", function(e) {
                    var nextURL = response.next;
                    getPackgaesList(nextURL);
                })


                

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

        if (status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST) {
            return response.json()
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function setToken(correctResponse) {
        window.localStorage.setItem("access_token", correctResponse.access_token);
        console.log("Set token correctly!")
        getPackgaesList(packages0URL);
    }



});