
var scrollable = document.getElementById('char-area');
function scrollToTop() {
    scrollable.scrollTop = scrollable.scrollHeight;
  }
  scrollToTop();

  
function msgValidation(event) {

  // Get the values of the message input and file input
  var msg_input = document.getElementById('msg').value.trim();
  var file_input = document.getElementById('file-input').files;
  let email = document.getElementById('email').checked;
  let popupmain = document.getElementById('emailpopup');
  let popupYes = document.getElementById('popup-yes')

  if (email == true ) {
    alert(popupYes.value)
    popupmain.style.display = 'flex';
    if(popupYes.value == 'Y'){
      if (msg_input !== '' || (file_input && file_input.length > 0)) { 
        return true;
      } else {
        // Return false if the validation fails
        return false;
      }
    }
    popupYes.value = 'Y'
    return false
  }
  
  // Check if either the message input is not empty or a file has been selected
  if (msg_input !== '' || (file_input && file_input.length > 0)) { 
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


