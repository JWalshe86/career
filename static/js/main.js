document.addEventListener("DOMContentLoaded", function(){
    var btn = document.getElementById("myBtn");
    var element = document.getElementById("myToast");

    // Create toast instance
    var myToast = new bootstrap.Toast(element);

    btn.addEventListener("click", function(){
        myToast.show();
    });
});
