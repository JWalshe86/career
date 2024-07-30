$(document).ready(function (){
$("li:contains(not_proceeding)").parents('.card').css('background-color', 'red');    
$("li:contains(None)").parents('.card').css('background-color', 'yellow');    


var $temp = $("<input>");
var $url = 'www.linkedin.com/in/john-walshe86';
var $url2 = 'https://github.com/JWalshe86/';
var $url3 = 'https://github.com/user-attachments/files/16346134/John_Walshe_CV.1.pdf';

$('.linkedin').on('click', function() {
  $("body").append($temp);
  $temp.val($url).select();
  document.execCommand("copy");
  $temp.remove();
  $("p").text("Linkedin URL copied!");
})

$('.github').on('click', function() {
  $("body").append($temp);
  $temp.val($url2).select();
  document.execCommand("copy");
  $temp.remove();
  $("p").text("Github URL copied!");
})

$('.cv').on('click', function() {
  $("body").append($temp);
  $temp.val($url3).select();
  document.execCommand("copy");
  $temp.remove();
  $("p").text("CV URL copied!");
})

})
