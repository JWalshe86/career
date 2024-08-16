$(document).ready(function (){

$("li:contains(not_proceeding)").parents('.card').css('background-color', 'red');    
$("li:contains(interview)").parents('.card').css('background-color', 'blue');    
$("li:contains(pre_int_screen)").parents('.card').css('background-color', '#83d7ad');    
$("li:contains(pending)").parents('.card').css('background-color', 'yellow');    
$("li:contains(offer)").parents('.card').css('background-color', 'green');    


$("li:contains(1week)").parents('.card').css('background-color', 'pink');    
$("li:contains(2week)").parents('.card').css('background-color', 'purple');    
$("li:contains(1month)").parents('.card').css('background-color', 'orange');    


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
//return dates

let elements = document.querySelectorAll('li');
      
var x = elements.forEach(element => {
                   addcreated_at(element)
		   })
console.log('x', x)

function addcreated_at(created_atElement){

        let data = created_atElement.dataset
        let date_applied = data.jobCreated_at
        return date_applied;
      }

// Function to check if one week has passed
function checkOneWeekPassed(startDate) {
    // Get the current date
    const currentDate = new Date();
    
    // Calculate the difference in time (in milliseconds)
    const timeDifference = currentDate - new Date(startDate);
    
    // Convert time difference to days
    const daysDifference = timeDifference / (1000 * 3600 * 24);
    
    // Check if the difference is greater than or equal to 7 days
    if (daysDifference >= 7) {
        alert("One week has passed!");
    }
    console.log('currentDate', currentDate)
}

// Example usage
const startDate = "2024-08-09"; // Replace with your start date
checkOneWeekPassed(startDate);


})






