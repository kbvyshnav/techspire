
var scrollable = document.getElementById('char-area');
function scrollToTop() {
    scrollable.scrollTop = scrollable.scrollHeight;
  }
  scrollToTop();

  
function msgValidation() {
  // Get the values of the message input and file input
  var msg_input = document.getElementById('msg').value.trim();
  var file_input = document.getElementById('file-input').files;

  // Check if either the message input is not empty or a file has been selected
  if (msg_input !== '' || (file_input && file_input.length > 0)) {
    // Return true if the validation is successful
    return true;
  } else {
    // Return false if the validation fails
    return false;
  }
}

// document.getElementById("msg").addEventListener("keydown", function(event) {
//   if (event.key === "Enter") {
//       event.preventDefault();  // Prevent newline (default behavior)
//       document.getElementById("messageForm").submit();  // Submit form
//   }
// });