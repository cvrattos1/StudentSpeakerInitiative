
// Tab graphics 
const tabs = document.querySelectorAll('[data-tab-target]')
const tabContents = document.querySelectorAll('[data-tab-content]' )
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = document.querySelector(tab.dataset.tabTarget)
        tabContents.forEach(tabContent => {
            tabContent.classList.remove('active')
        })
        tabs.forEach(tab => {
            tab.classList.remove('active')
        })
        tab.classList.add('active')
        target.classList.add('active')
    })
}) 


// Nominating 
function getNom() {
    var fname = document.getElementById("fname").value
    var lname = document.getElementById("lname").value
    var descrip = document.getElementById("descrip").value
    var wiki = document.getElementById("wiki").value
    var photo = document.getElementById("photo").value
    
    // show image 
    var img = document.createElement("img");
    img.src = photo;
    var src = document.getElementById("x");
    src.appendChild(img);
    
    document.getElementById("name_display").innerHTML = "Name: " + fname + " " + lname
    document.getElementById("descrip_display").innerHTML = "Description: " + descrip    
    document.getElementById("wiki_display").innerHTML = "Wiki Link: " + wiki

    document.getElementById("nom-button").style.display = "none"
    alert("Nomination submitted.")
}

