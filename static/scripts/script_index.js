document.addEventListener("DOMContentLoaded", function(event) {
    var table = document.getElementsByClassName("color-table")[0];
    table.addEventListener("mouseover", function(){
        var rows = document.getElementsByClassName("tbody_packages")[0].getElementsByTagName("tr");
        for (var i = 0; i < rows.length; i++){
            if (i%2 == 0){
                rows[i].style.backgroundColor = "#F5DEB3";
            } else {
                rows[i].style.backgroundColor = "#C0C0C0";
            }
        }
    });

    table.addEventListener("mouseout", function(){
        var rows = document.getElementsByClassName("tbody_packages")[0].getElementsByTagName("tr");
        for (var i = 0; i < rows.length; i++){
            if (i%2 == 0){
                rows[i].style.backgroundColor = "#DCDCDC";
            } else {
                rows[i].style.backgroundColor = "#FFEFD5";
            }
        }
    });
});
