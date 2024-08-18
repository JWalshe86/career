dy(function () {

    // Change background color based on status
    $("li:contains(not_proceeding)").parents('.card').css('background-color', 'red');
    $("li:contains(interview)").parents('.card').css('background-color', 'blue');
    $("li:contains(pre_int_screen)").parents('.card').css('background-color', '#83d7ad');
    $("li:contains(pending)").parents('.card').css('background-color', 'yellow');
    $("li:contains(offer)").parents('.card').css('background-color', 'green');

    $("li:contains(1week)").parents('.card').css('background-color', 'pink');
    $("li:contains(2week)").parents('.card').css('background-color', 'purple');
    $("li:contains(1month)").parents('.card').css('background-color', 'orange');

    // Copy URL to clipboard and show message
    $('.linkedin').on('click', function() {
        copyToClipboard('www.linkedin.com/in/john-walshe86', "LinkedIn URL copied!");
    });

    $('.github').on('click', function() {
        copyToClipboard('https://github.com/JWalshe86/', "GitHub URL copied!");
    });

    $('.cv').on('click', function() {
        copyToClipboard('https://github.com/user-attachments/files/16346134/John_Walshe_CV.1.pdf', "CV URL copied!");
    });

    function copyToClipboard(url, message) {
        var $temp = $("<input>");
        $("body").append($temp);
        $temp.val(url).select();
        document.execCommand("copy");
        $temp.remove();
        $("p").text(message);
    }

    function checkOneWeekPassed(dateapplied, element) {
        const currentDate = new Date();
        const timeDifference = currentDate - new Date(dateapplied);
        const daysDifference = timeDifference / (1000 * 3600 * 24);

        // Change the status to '1week' 
dy(function () {

    // Function to check if one week has passed and update the status
    function checkOneWeekPassed(dateapplied, element) {
        const currentDate = new Date();
        const appliedDate = new Date(dateapplied);
        const timeDifference = currentDate - appliedDate;
        const daysDifference = timeDifference / (1000 * 3600 * 24);

        // If a week has passed, update the text from 'pending' to '1week'
        if (daysDifference >= 7) {
            element.text(function(index, text) {
                return text.replace('pending', '1week');
            });
            element.parents('.card').css('background-color', 'pink');
        }
    }

    // Select all list items containing the word "pending"
    $("li:contains(pending)").each(function() {
        let element = $(this);

        // Retrieve the 'data-dateapplied' attribute
        let dateapplied = element.attr('data-dateapplied');

        // Check if a week has passed and update the status and color if so
        if (dateapplied) {
            checkOneWeekPassed(dateapplied, element);
        }
    });

});

