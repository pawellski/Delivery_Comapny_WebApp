document.addEventListener('DOMContentLoaded', function (event) {
    var HTTP_STATUS = {OK: 200};
    var URL = "https://localhost:8080/get_token";
    var GET = "GET";

    get_token();



    function get_token() {
        let params = {
            method: GET,
            redirect: "follow"
        }
        
        fetch(URL, params)
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