 // Function to change webpage background color
 function defaultTheme(){
    document.getElementById("friends").style.background = '#89cfef';
    document.getElementById("friendonlinetext").style.color = '#1c2951';
    document.body.style.background = '#cdb7f6';

    for(let i=0; i<=4; i++){ document.getElementById("friendtile"+i).style.background = '#d0f0c0'; }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#89cfef';
        document.getElementById("t"+i).style.color = '#d0f0c0';
        document.getElementById("b"+i).style.color = '#d0f0c0';
    }
}

function spotifyTheme(){
    document.getElementById("friends").style.background = '#ffffff';
    document.getElementById("friendonlinetext").style.color = 'black';
    for(let i=0; i<=4; i++){
        document.getElementById("friendtile"+i).style.background = '#2b856b';
    }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#003245';
        document.getElementById("t"+i).style.color = '#1db954';
        document.getElementById("b"+i).style.color = '#1db954';
    }
    document.body.style.background = 'black';
}
 
 function countryTheme(){
    document.getElementById("friends").style.background = '#fffdd0';
    document.getElementById("friendonlinetext").style.color = '#420d09';
    for(let i=0; i<=4; i++){
        document.getElementById("friendtile"+i).style.background = '#997950';
    }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#f8e473';
        document.getElementById("t"+i).style.color = '#a45a52';
        document.getElementById("b"+i).style.color = '#a45a52';
    }
    document.body.style.background = '#420d09';
}

function rapTheme(){
    document.getElementById("friends").style.background = '#191414';
    document.getElementById("friendonlinetext").style.color = '#d9dddc';
    for(let i=0; i<=4; i++){
        document.getElementById("friendtile"+i).style.background = '#800000';
    }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#800000';
        document.getElementById("t"+i).style.color = '#d9dddc';
        document.getElementById("b"+i).style.color = '#d9dddc';
    }
    document.body.style.background = '#777b7e';
}

function popTheme(){
    document.getElementById("friends").style.background = '#ffffff';
    document.getElementById("friendonlinetext").style.color = '#003245';
    document.body.style.background = '#003245';

    for(let i=0; i<=4; i++){ document.getElementById("friendtile"+i).style.background = '#0080fe'; }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#ffffff';
        document.getElementById("t"+i).style.color = '#0080fe';
        document.getElementById("b"+i).style.color = '#0080fe';
    }
}

function rnbTheme(){
    document.getElementById("friends").style.background = '#8f00ff';
    document.getElementById("friendonlinetext").style.color = '#fec5e5';
    document.body.style.background = '#000080';

    for(let i=0; i<=4; i++){ document.getElementById("friendtile"+i).style.background = '#fec5e5'; }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#8f00ff';
        document.getElementById("t"+i).style.color = '#fec5e5';
        document.getElementById("b"+i).style.color = '#fec5e5';
    }
}

function lofiTheme(){
    document.getElementById("friends").style.background = '#89cfef';
    document.getElementById("friendonlinetext").style.color = '#1c2951';
    document.body.style.background = '#cdb7f6';

    for(let i=0; i<=4; i++){ document.getElementById("friendtile"+i).style.background = '#d0f0c0'; }
    for(let i=1; i<=3; i++){
        document.getElementById("p"+i).style.background = '#89cfef';
        document.getElementById("t"+i).style.color = '#d0f0c0';
        document.getElementById("b"+i).style.color = '#d0f0c0';
    }
}