// $(document).ready(function () {

//     // Create a temporary input field for copying URLs
//     var $temp = $("<input>");

//     // URL variables
//     var $url = 'www.linkedin.com/in/john-walshe86';
//     var $url2 = 'https://github.com/JWalshe86/';
//     var $url3 = 'https://github.com/user-attachments/files/16346134/John_Walshe_CV.1.pdf';

//     // Copy Linkedin URL to clipboard
//     $('.linkedin').on('click', function() {
//         $("body").append($temp);
//         $temp.val($url).select();
//         document.execCommand("copy");
//         $temp.remove();
//         $("p").text("LinkedIn URL copied!");
//     });

//     // Copy GitHub URL to clipboard
//     $('.github').on('click', function() {
//         $("body").append($temp);
//         $temp.val($url2).select();
//         document.execCommand("copy");
//         $temp.remove();
//         $("p").text("GitHub URL copied!");
//     });

//     // Copy CV URL to clipboard
//     $('.cv').on('click', function() {
//         $("body").append($temp);
//         $temp.val($url3).select();
//         document.execCommand("copy");
//         $temp.remove();
//         $("p").text("CV URL copied!");
//     });
// });

