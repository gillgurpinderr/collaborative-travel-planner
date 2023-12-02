// Function to Open Popup
document.getElementById("popupFormButton").onclick = function() {
    document.getElementById("popupForm").style.display = "block";
}

// Function to Close Popup
function closePopup() {
    document.getElementById("popupForm").style.display = "none";
}

// Function to Open Popup
document.getElementById("popupFormButton").onclick = function() {
    document.getElementById("popupForm").style.display = "block";
};

// Function to Close Popup
function closePopup() {
    document.getElementById("popupForm").style.display = "none";
};

// Function to Add a Member
function addMember() {
    var firstName = document.getElementById("firstName").value;
    var lastName = document.getElementById("lastName").value;
    if (firstName && lastName) {
        var membersList = document.getElementById("membersList");
        var li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `${firstName} ${lastName} 
                        <button class="btn btn-sm btn-info" onclick="editMember(this)">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteMember(this)">Delete</button>`;
        membersList.appendChild(li);
        // Clear input fields
        document.getElementById("firstName").value = '';
        document.getElementById("lastName").value = '';
    } else {
        alert("Please enter both first and last names.");
    }
};

// Function to Delete a Member
function deleteMember(button) {
    var li = button.parentElement;
    li.remove();
};

// Function to Edit a Member
function editMember(button) {
    var li = button.parentElement;
    var names = li.firstChild.textContent.split(" ");
    var firstName = prompt("Edit First Name:", names[0]);
    var lastName = prompt("Edit Last Name:", names[1]);

    if (firstName != null && lastName != null) {
        li.firstChild.textContent = `${firstName} ${lastName} `;
        li.appendChild(button.nextSibling); // Append Edit button
        li.appendChild(button); // Append Delete button
    }
};
