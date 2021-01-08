document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, UNAUTHORIZED: 401};
    
    var packages0URL = "https://localhost:8083/packages/list/0";
    var GET = "GET";

    const PICKUP_PACKAGE_ROOM = "pickup-package-room";

    let alertDiv = document.getElementById("alert-div-courier-packages");
    let currentPackagesURL = packages0URL;

    var ws_uri = "https://localhost:8082";
    socket = io.connect(ws_uri);
    joinIntoRoom(PICKUP_PACKAGE_ROOM);

    socket.on("connect", function () {
        console.log("Correctly connected to the chat");
    });

    socket.on("joined_room", function (message) {
        console.log("Joined to the room ", message);
    });

    socket.on("chat_message", function (data) {
        console.log("Received new chat message:", data);
        getPackagesList(currentPackagesURL);
        let text = document.createTextNode("Pojawiły się nowe paczki do dostarczenia.")
        let warning = document.createElement("div");
        warning.setAttribute("class", "alert alert-warning");
        warning.setAttribute("role", "alert");
        warning.appendChild(text)
        alertDiv.appendChild(warning);
    });

    function joinIntoRoom(room_id) {
        socket.emit("join", {room_id: room_id });
    }

    getPackagesList(packages0URL);

    function getPackagesList(URL) {
        alertDiv.innerHTML = "";
        currentPackagesURL = URL;

        let params = {
            method: GET,
            redirect: "follow"
        };

        fetch(URL, params)
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
        } else if(status === HTTP_STATUS.UNAUTHORIZED) {
            window.location.href = "/login/";
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayTableWithPackages(response) {
        response = JSON.parse(response);
        let packagesElem = document.getElementById("packages");
        let numberOfPackages = response.numberOfPackages;

        packagesElem.innerHTML = "";
        let title = document.createElement("h2");
        title.setAttribute("class", "text-center");
        let titleText = document.createTextNode("MOJE PACZKI");
        title.appendChild(titleText);
        packagesElem.appendChild(title);

        if(numberOfPackages != 0) {
            let tableElem = document.createElement("table");
            tableElem.setAttribute("class", "table table-striped")
            tableElem.setAttribute("id", "available-packages-table");
            let tableHeadElem = document.createElement("thead");
            let tableBodyElem = document.createElement("tbody");
            let trHead = document.createElement("tr");
            let th = document.createElement("th");
            th.setAttribute("scope", "col");
            thText = document.createTextNode("Numer paczki");
            th.appendChild(thText);
            trHead.appendChild(th);
            tableHeadElem.appendChild(trHead);
            
            for (var i = 0; i < response.packages.length; i++) {
                let row = document.createElement("tr");
                let cell = document.createElement("td");
                let text = document.createTextNode(response.packages[i].id);
                cell.appendChild(text);
                row.appendChild(cell);
                tableBodyElem.appendChild(row);
            }

            tableElem.appendChild(tableHeadElem);
            tableElem.appendChild(tableBodyElem);
            packagesElem.appendChild(tableElem);

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

            packagesElem.appendChild(paginationUl);

            let hr = document.createElement("hr");
            packagesElem.appendChild(hr);

            let numberOfPackagesContent = document.createTextNode("Liczba paczek do dostarczenia: " + numberOfPackages);
            let numberOfPackagesElem = document.createElement('h6');
            numberOfPackagesElem.setAttribute("id", "numberOfPackages");
            numberOfPackagesElem.setAttribute("class", "text-center font-weight-bold");
            numberOfPackagesElem.appendChild(numberOfPackagesContent);
            packagesElem.appendChild(numberOfPackagesElem);

        } else {
            let lackOfPackagesElem = document.createElement('h3');
            let lackOfPackagesContent = document.createTextNode("Aktulnie nie posiadasz paczek do rozwiezienia.");
            lackOfPackagesElem.setAttribute("class", "text-center h3-head");
            lackOfPackagesElem.setAttribute("id", "lackOfPackages");
            lackOfPackagesElem.appendChild(lackOfPackagesContent);
            packagesElem.appendChild(lackOfPackagesElem);
        }
    }
});