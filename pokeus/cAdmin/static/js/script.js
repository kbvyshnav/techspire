const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});




// // TOGGLE SIDEBAR
// const menuBar = document.querySelector('#content nav .bx.bx-menu');
// const sidebar = document.getElementById('sidebar');

// menuBar.addEventListener('click', function () {
// 	sidebar.classList.toggle('hide');
// })


// profile toggleMenu dropdown	
function toggleMenu() {
	let subMenu = document.getElementById("subMenu");
    subMenu.classList.toggle("open-menu");

	document.addEventListener('click', closeMenuOnClickOutside);
}

// function closeMenuOnClickOutside(event) {
//     let subMenu = document.getElementById("subMenu");
//     if (!subMenu.contains(event.target)) {
//         // If the click is outside the menu, close the menu
//         subMenu.classList.remove("open-menu");
//         document.removeEventListener('click', closeMenuOnClickOutside);
//     }
// }
	
// $('#open-menu').click(function(e) {
//     e.stopPropagation();
//     $(this).fadeOut(300);
// });
	
// window.addEventListener('mouseup', function(e) {
//     var x = document.querySelector('#mylinks');
//     if (event.target != document.querySelector(".icon")) {
//         x.style.display = "none";
//     }
// });	

// if(window.innerWidth < 768) {
// 	sidebar.classList.add('hide');
// } else if(window.innerWidth > 576) {
// 	searchButtonIcon.classList.replace('bx-x', 'bx-search');
// 	searchForm.classList.remove('show');
// }


// window.addEventListener('resize', function () {
// 	if(this.innerWidth > 576) {
// 		searchButtonIcon.classList.replace('bx-x', 'bx-search');
// 		searchForm.classList.remove('show');
// 	}
// })



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}
})


// Functions for ticket utilities

function priority(tno){
	var priority = document.getElementById('tpriority' + tno).value;
	var result = null;
	if ( priority == 'HIGH' ){
		result = 'High';
	}
	else if ( priority == 'Medium'){
		result = 'Medium';
	}
	else{
		result = 'Low';
	}
	return result;
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

function search_validator(){
	var frmdte = document.getElementById("fromDateInput").value;
	var todte = document.getElementById('toDateInput').value;
	var srchbx= document.getElementById('keyword').value.trim();
	if(srchbx == null || srchbx == '' ){
	if (frmdte == '' && todte == ''  ){
		alert('Please select date!');
		return false;
	}
	else{
		if(frmdte > todte){
			alert("The 'from' date shouldn't overlap with the 'to' date.");
			return false;
		}
		else{
		return true;
		}
	}}
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

function cur_holder(tno){
	var dev_id = 'tdevs' + tno;
	var tstr_id = 'ttester' + tno;
	var usr_id = 'tmaker' + tno;
	var stat_id = 'tstatus' + tno;
	var dev_id_val = document.getElementById(dev_id).value;
	var tstr_id_val = document.getElementById(tstr_id).value;
	var usr_id_val = document.getElementById(usr_id).value;
	var stat_id_val = document.getElementById(stat_id).value;
	var prefix = '';
	
	
	if( stat_id_val === 'TA' && dev_id_val !== '' && tstr_id_val ==='') {
		return (prefix + ' ' + dev_id_val + '');
	}
	else if ( stat_id_val === 'DA' && dev_id_val !== '' && tstr_id_val == ''){
		return (prefix + ' ' + dev_id_val + '' );
	}
	else if ( stat_id_val === 'DA' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix + ' ' + dev_id_val + '' );
	}
	else if ( stat_id_val === 'EP' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix + ' ' + tstr_id_val + '');
	}
	else if ( stat_id_val === 'EA' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix +' ' + tstr_id_val + '');
	}
	else if ( stat_id_val === 'RL' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix + ' ' + dev_id_val + '');
	}
	else if ( stat_id_val === 'RA' && dev_id_val !== '' && tstr_id_val === ''){
		return (prefix + ' ' + dev_id_val + '');
	}
	else if ( stat_id_val === 'TH' && dev_id_val !== '' && tstr_id_val === ''){
		return (prefix + ' ' + usr_id_val + '');
	}
	else if ( stat_id_val == 'PC' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix + ' ' + dev_id_val + '' );
	}
	else if ( stat_id_val === 'BP' && dev_id_val !== '' && tstr_id_val !== ''){
		return (prefix +' ' + dev_id_val + '' );
	}
	else if( stat_id_val === 'TA' && dev_id_val !== '' && tstr_id_val !=='') {
		return (prefix + ' ' + dev_id_val + '');
	}
	
	else {
		
		return null;
	}
	
}

function srch_data_keeper(cmpny_name,prev_date,to_date,searchkey){


	var companyDropdown = document.getElementById('companyDropdown');
	var frm_element =  document.getElementById('fromDateInput');
	var to_element = document.getElementById('toDateInput');
	var srch_box_val = document.getElementById('keyword');
	srch_box_val.value = searchkey;
	frm_element.value = prev_date;
	to_element.value = to_date;



    // Loop through the options and set the selected attribute for the matching option
    for (var i = 0; i < companyDropdown.options.length; i++) {
        if (companyDropdown.options[i].value == cmpny_name) {
            companyDropdown.options[i].selected = true;
            break;  // Stop the loop once a match is found
        }
    }



}


// function DaysToDate(dateString, numberOfDaysToAdd) { 
//   if(numberOfDaysToAdd != 'None')
//   if(dateString != null){    
//   var dateParts = dateString.split("-");
//   var year = parseInt(dateParts[2], 10);
//   var month = parseInt(dateParts[1], 10) - 1; // Months are zero-based
//   var day = parseInt(dateParts[0], 10);

//   var originalDate = new Date(year, month, day);

//   // Calculate the new date by adding the number of days
//   var newDate = new Date(originalDate);
//   newDate.setDate(originalDate.getDate() + numberOfDaysToAdd);

//   // Convert the new date back to a string in "dd-mm-yyyy" format
//   var newDateString =
//     newDate.getDate().toString().padStart(2, "0") +
//     "-" +
//     (newDate.getMonth() + 1).toString().padStart(2, "0") +
//     "-" +
//     newDate.getFullYear();

//     return newDateString;
//   }
//   else{
//      alert('null retutn');
//      return ' ';
//   }
  
// }

function DaysToDate(dateString, numberOfDaysToAdd) { 
  if (numberOfDaysToAdd !== 'None') {
  
      var dateParts = dateString.split("-");
      var year = parseInt(dateParts[2], 10);
      var month = parseInt(dateParts[1], 10) - 1; // Months are zero-based
      var day = parseInt(dateParts[0], 10);

      var originalDate = new Date(year, month, day);

      // Calculate the new date by adding the number of days
      var newDate = new Date(originalDate);
      newDate.setDate(originalDate.getDate() + parseInt(numberOfDaysToAdd, 10));

      // Convert the new date back to a string in "dd-mm-yyyy" format
      var newDateString =
        newDate.getDate().toString().padStart(2, "0") +
        "-" +
        (newDate.getMonth() + 1).toString().padStart(2, "0") +
        "-" +
        newDate.getFullYear();

      return newDateString;
   
    }
   else {
   
    return ' ';
  }
}



function onChangeValidator(){

	if( search_validator()){
		cmpny_drpdwn_validator();
		document.getElementById('search_panel').submit() ;
	}
} 




function toggleNotifications() {
    var notificationMenu = document.getElementById("notificationMenu");
    notificationMenu.classList.toggle("open-menu"); /* Toggle the visibility */
}

