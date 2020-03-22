
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
    // var img = document.createElement("img");
    // img.src = photo;
    // var src = document.getElementById("x");
    // src.appendChild(img);

    // document.getElementById("name_display").innerHTML = "Name: " + fname + " " + lname
    // document.getElementById("descrip_display").innerHTML = "Description: " + descrip    
    // document.getElementById("wiki_display").innerHTML = "Wiki Link: " + wiki

    // bug - doesn't work in chrome 
    delete window.alert; 
    alert("Nomination submitted.")
    document.getElementById("nom-button").style.display = "none"
    
}

// Endorsing 
endorsements_left = 5 
endorsements_gained = 0
function endorse() {
    if (endorsements == 0){
        alert("No more endorsements left")
    }
    else {
        endorsements_gained = endorsements_gained + 1
        endorsements = endorsements - 1
        document.getElementById("endorse_count").innerHTML = "count: " + endorsements_gained
        alert(endorsements + "left")
    }
    
}
function report() {
    alert("Report will be reviewed soon.")

}

