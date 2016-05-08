// Allows a new category to be added when "New Category" is selected from dropdown
function newCategory(that) {
    // Check that "New Category" was selected by user
    if (that.value == "newCategory") {
        // Show hidden manual entry
        document.getElementById("ifNewCategory").style.display = "block";
    } else {
        document.getElementById("ifNewCategory").style.display = "none";
    }
}
