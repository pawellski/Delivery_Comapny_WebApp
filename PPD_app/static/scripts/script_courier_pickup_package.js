document.addEventListener('DOMContentLoaded', function (event) {

    var pickupPackageURL = "https://localhost:8083/pickup_package/";
    var tokenURL = "https://localhost:8083/token/"
    var HTTP_STATUS = {OK: 200, BAD_REQUEST: 400, UNAUTHORIZED: 401, CONFLICT: 409};
    var POST = "POST";

    var passOnPackageForm = document.getElementById("passon-package-form");
    var getTokenForm = document.getElementById("get-token-form");

    const PASSON_PACKAGE_ROOM = "passon-package-room";

    var ws_uri = "https://localhost:8084";
    
    socket = io.connect(ws_uri);
    joinIntoRoom(PASSON_PACKAGE_ROOM);

    socket.on("connect", function () {
        console.log("Correctly connected to the chat");
    });

    socket.on("joined_room", function (message) {
        console.log("Joined to the room ", message);
    });

    socket.on("chat_message", function (data) {
        console.log("Received new chat message:", data);

    });

    function joinIntoRoom(room_id) {
        socket.emit("join", {room_id: room_id });
    }

    function sendMessage(room_id, text) {
        data = { room_id: room_id, message: text };
        socket.emit("new_message", data);
    }


    passOnPackageForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Pass On Package Form Submission stopped.");

        submitPassOnPackage();
    });

    getTokenForm.addEventListener("submit", function(event) {
        event.preventDefault();

        console.log("Get Token Form Submission stopped.");

        submitGetToken();
    });

    function submitPassOnPackage() {
        let packageParams = {
            method: POST,
            body: new FormData(passOnPackageForm),
            redirect: "follow"
        }

        fetch(pickupPackageURL, packageParams)
            .then(response => getPassOnPackageResponse(response))
            .then(response => displayAlert2(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });

    }

    function submitGetToken() {
        let tokenParams = {
            method: POST,
            body: new FormData(getTokenForm),
            redirect: "follow"
        }
        
        fetch(tokenURL, tokenParams)
            .then(response => getTokenResponseData(response))
            .then(response => displayAlert1(response))
            .catch(err => {
                console.log("Caught error: " + err)
            });

    }

    function getPassOnPackageResponse(response) {
        let status = response.status;
        console.log(status);
        if(status === HTTP_STATUS.OK || status === HTTP_STATUS.BAD_REQUEST || status === HTTP_STATUS.CONFLICT) {
            return response.status
        } else if(status === HTTP_STATUS.UNAUTHORIZED) {
            window.location.href = "/login/";
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function getTokenResponseData(response) {
        let status = response.status;

        if(status == HTTP_STATUS.OK || status == HTTP_STATUS.BAD_REQUEST) {
            return response.json()
        } else if(status === HTTP_STATUS.UNAUTHORIZED) {
            window.location.href = "/login/";
        } else {
            console.error("Response status code: " + response.status);
            throw "Unexcepted response status: " + response.status;
        }
    }

    function displayAlert2(status) {
        let alertDiv = document.getElementById("alert-div-2");
        alertDiv.innerHTML = ""
        if (status == 200) {
            let text = document.createTextNode("Proces przekazania paczki przebiegł pomyślnie.")
            alertDiv.setAttribute("class", "alert alert-success");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
            sendMessage(PASSON_PACKAGE_ROOM, "Packages updated! - Pass on package by courier.");
        } else if (status == 400) {
            let text = document.createTextNode("Paczka o podanym numerze nie istnieje.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else if (status == 409){
            let text = document.createTextNode("Paczka nie może zostać przekazana, ponieważ proces jej dostawy jest w toku.")
            alertDiv.setAttribute("class", "alert alert-warning");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        }

    }

    function displayAlert1(response) {
        let alertDiv = document.getElementById("alert-div-1");
        alertDiv.innerHTML = "";
        if (response.token == "True") {
            let access_token = response.access_token
            let message = "Kod dostępu do paczkomatu: " + access_token;
            let text = document.createTextNode(message)
            alertDiv.setAttribute("class", "alert alert-success");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        } else {
            let text = document.createTextNode("Paczkomat o podanym numerze nie istnieje.")
            alertDiv.setAttribute("class", "alert alert-danger");
            alertDiv.setAttribute("role", "alert");
            alertDiv.appendChild(text);
        }

    }

});