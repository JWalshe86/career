$(document).ready(function (){
$("li:contains(not_proceeding)").parents('.card').css('background-color', 'red');    
$("li:contains(None)").parents('.card').css('background-color', 'yellow');    
})
