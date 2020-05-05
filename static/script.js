function updateNav(validation) {
    console.log("hello")
    if ("{{validation['nominating']}}" == "True") {
        $(document.getElementById("navNom")).addClass("btn-success font-weight-bold");
        $(document.getElementById("navEndorse")).addClass("btn-info font-weight-bold");
        $(document.getElementById("navVote")).addClass("btn-outline-light disabled");
        $(document.getElementById("navResults")).addClass("btn-outline-light disabled");
    }
    else if ("{{validation['endorsing']}}" == "True") {
        $(document.getElementById("navNom")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navEndorse")).addClass("btn-success font-weight-bold");
        $(document.getElementById("navVote")).addClass("btn-outline-light disabled");
        $(document.getElementById("navResults")).addClass("btn-outline-light disabled");
    }
    else if ("{{validation['voting']}}" == "True") {
        $(document.getElementById("navNom")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navEndorse")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navVote")).addClass("btn-success font-weight-bold");
        $(document.getElementById("navResults")).addClass("btn-outline-light disabled");
    }
    else if ("{{validation['results']}}" == "True") {
        $(document.getElementById("navNom")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navEndorse")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navVote")).addClass("btn-outline-danger disabled");
        $(document.getElementById("navResults")).addClass("btn-success font-weight-bold");
    }
    else {
        $(document.getElementById("navNom")).addClass("btn-outline-light disabled");
        $(document.getElementById("navEndorse")).addClass("btn-outline-light disabled");
        $(document.getElementById("navVote")).addClass("btn-outline-light disabled");
        $(document.getElementById("navResults")).addClass("btn-outline-light disabled");
    }
}
