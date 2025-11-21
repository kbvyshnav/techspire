function user_form_validator(){
    form = document.getElementById('user_form');
    var page_id = document.createElement('input');
    page_id.type = 'hidden';
    page_id.name = 'page_id';
    page_id.value = document.getElementById('page_id').value;
    form.appendChild(page_id);
    return true;
}

// profile toggleMenu dropdown	
function toggleMenu() {
	let subMenu = document.getElementById("subMenu");
    subMenu.classList.toggle("open-menu");

	document.addEventListener('click', closeMenuOnClickOutside);
}

function cmpny_drpdwn_validator(){
	// alert('wrkd')
	// var srch_frm = document.getElementById('search_panel');
	// var drp_dwn_val = document.getElementById('companyDropdown').value;
	// var search_drpdwn_btn =document.getElementById('search_drpdwn_btn');
	// search_drpdwn_btn.value = 'D';
	// if( drp_dwn_val != '*'){
		// alert('wrkd'+drp_dwn_val+ document.getElementById('page_id').value)
		document.getElementById('page_id_val').value = document.getElementById('page_id').value;
		// alert(document.getElementById('page_id_val').value)


		// return true;
	// }

	return true;
	
}

function ticket_search() {
	// Get the value of the column (input) by its ID
	var columnValue = document.getElementById('keyword').value;
	// Check if the column is null or empty
	
	if (!columnValue.trim() ) {
		// If it is empty, prevent form submission and show an alert
		alert("Enter ticket ID!");
		return false;
	}
	
	
	// Check for special characters using a regular expression
	var specialCharacters = /[!@#$%^&*(),.?":{}|<>/+\-=]/;
	if (specialCharacters.test(columnValue) ) {
		// If there are special characters, prevent form submission and show an alert
		alert("Column cannot contain special characters!");
		return false;
	}
	// If the column has a value and doesn't contain special characters, allow form submission
	document.getElementById('page_id_val').value = document.getElementById('page_id').value;
	 document.getElementById('key').value='t';
	
	return true;
	// If the column has a value, allow form submission
	
}

function srch_data_keeper(prev_date,to_date,searchkey){



	var frm_element =  document.getElementById('fromDateInput');
	var to_element = document.getElementById('toDateInput');
	var srch_box_val = document.getElementById('keyword');
	srch_box_val.value = searchkey;
	frm_element.value = prev_date;
	to_element.value = to_date;



}

function DaysToDate(dateString, numberOfDaysToAdd) { 

  var dateParts = dateString.split("-");
  var year = parseInt(dateParts[2], 10);
  var month = parseInt(dateParts[1], 10) - 1; // Months are zero-based
  var day = parseInt(dateParts[0], 10);

  var originalDate = new Date(year, month, day);

  // Calculate the new date by adding the number of days
  var newDate = new Date(originalDate);
  newDate.setDate(originalDate.getDate() + numberOfDaysToAdd);

  // Convert the new date back to a string in "dd-mm-yyyy" format
  var newDateString =
    newDate.getDate().toString().padStart(2, "0") +
    "-" +
    (newDate.getMonth() + 1).toString().padStart(2, "0") +
    "-" +
    newDate.getFullYear();

  
  return newDateString;
}


function toggleNotifications() {
    var notificationMenu = document.getElementById("notificationMenu");
    notificationMenu.classList.toggle("open-menu"); /* Toggle the visibility */
}
