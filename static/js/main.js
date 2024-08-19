$(document).ready(function (){
$("li:contains(pending<wk)").parents('.card').css('background-color', 'yellow');    
$("li:contains(pending<2wk)").parents('.card').css('background-color', 'orange');    
$("li:contains(pend<MONTH)").parents('.card').css('background-color', 'purple');    
$("li:contains(not_proceeding)").parents('.card').css('background-color', 'red');    
$("li:contains(pre_int_screen)").parents('.card').css('background-color', '#83d7ad');    
$("li:contains(interview)").parents('.card').css('background-color', 'blue');    
$("li:contains(offer)").parents('.card').css('background-color', 'green');    


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
