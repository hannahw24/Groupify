<<<<<<< HEAD
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
=======

function defaultTheme(){
    const back_black = '#191414';
    const back_green = '#4FE383';
    const soft_green = '#4FE383';
    const tile_white = 'white';
    const text_black = '#221B1B';

    // change background of profile page to gradient of green to black
    document.body.style.backgroundImage = 'linear-gradient('+back_green+','+back_black +')';

    // change background of friend side bar white, text to black
    document.getElementById("friendbar").style.backgroundColor = tile_white;
    document.getElementById("follwingfriendtitle").style.color = back_black;

    // change each friend tile to green 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = soft_green;
        document.getElementsByClassName("friendname")[i].style.color = text_black;
        document.getElementsByClassName("friendtext")[i].style.color = text_black;
>>>>>>> cdc9f8e6a6876076ec85d686afe6a1d9ed80d366
    }

    // change each profile and bio tile to white
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = tile_white;
    }
    // change side group button to white
    document.getElementById("groupSideButton").style.backgroundColor = tile_white; 
}

<<<<<<< HEAD
function rapTheme(){
    document.getElementById("friends").style.background = '#191414';
    document.getElementById("friendonlinetext").style.color = '#d9dddc';
    for(let i=0; i<=4; i++){
        document.getElementById("friendtile"+i).style.background = '#800000';
=======
 function countryTheme(){
    const back_brown = '#420d09';
    const back_yellow = '#f8e473';
    const friend_brown = '#A07E54';
    const soft_yellow = '#FFFDD6';
    const text_white = 'white';

    // change background of profile page to gradient of red to black
    document.body.style.backgroundImage = 'linear-gradient('+back_yellow+','+back_brown +')';

    // change background of friend side bar metal-gray, text to ______
    document.getElementById("friendbar").style.backgroundColor = soft_yellow;
    document.getElementById("follwingfriendtitle").style.color = '#191414';

    // change each friend tile to soft red 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = friend_brown;
        document.getElementsByClassName("friendname")[i].style.color = text_white;
        document.getElementsByClassName("friendtext")[i].style.color = text_white;
>>>>>>> cdc9f8e6a6876076ec85d686afe6a1d9ed80d366
    }

    // change each profile and bio tile to metal-gray
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = soft_yellow;
    }
    // change side group button to metal-gray
    document.getElementById("groupSideButton").style.backgroundColor = soft_yellow; 
}

<<<<<<< HEAD
=======
function rapTheme(){
    const back_black = '#191414';
    const back_red = '#800000';
    const soft_red = '#993333';
    const metal_gray = '#919191';
    const text_white = 'white';

    // change background of profile page to gradient of red to black
    document.body.style.backgroundImage = 'linear-gradient('+back_red+','+back_black +')';

    // change background of friend side bar metal-gray, text to ______
    document.getElementById("friendbar").style.backgroundColor = metal_gray;
    document.getElementById("follwingfriendtitle").style.color = '#191414';

    // change each friend tile to soft red 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = soft_red;
        document.getElementsByClassName("friendname")[i].style.color = text_white;
        document.getElementsByClassName("friendtext")[i].style.color = text_white;
    }

    // change each profile and bio tile to metal-gray
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = metal_gray;
    }
    // change side group button to metal-gray
    document.getElementById("groupSideButton").style.backgroundColor = metal_gray; 
}

>>>>>>> cdc9f8e6a6876076ec85d686afe6a1d9ed80d366
function popTheme(){
    const back_pink = '#ffaff6';
    const back_blue = '#0080fe';
    const white = 'white';
    const text_black = '#221B1B';

    // change background of profile page to gradient of red to black
    document.body.style.backgroundImage = 'linear-gradient('+back_pink+' 25%,'+back_blue +')';

    // change background of friend side bar metal-gray, text to ______
    document.getElementById("friendbar").style.backgroundColor = white;
    document.getElementById("follwingfriendtitle").style.color = '#191414';

    // change each friend tile to soft red 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = back_pink;
        document.getElementsByClassName("friendname")[i].style.color = text_black;
        document.getElementsByClassName("friendtext")[i].style.color = text_black;
    }

    // change each profile and bio tile to metal-gray
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = white;
    }
    // change side group button to metal-gray
    document.getElementById("groupSideButton").style.backgroundColor = white; 
}

function rnbTheme(){
    const back_black = '#12006e';
    const back_vio = '#942ec8';
    const friend_purple = '#8961d8';
    const tile_pink = '#d9dddc';
    const text_black = '#221B1B';

    // change background of profile page to gradient of red to black
    document.body.style.backgroundImage = 'linear-gradient('+back_vio+','+back_black +')';

    // change background of friend side bar metal-gray, text to ______
    document.getElementById("friendbar").style.backgroundColor = tile_pink;
    document.getElementById("follwingfriendtitle").style.color = '#191414';

    // change each friend tile to soft red 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = friend_purple;
        document.getElementsByClassName("friendname")[i].style.color = text_black;
        document.getElementsByClassName("friendtext")[i].style.color = text_black;
    }

    // change each profile and bio tile to metal-gray
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = tile_pink;
    }
    // change side group button to metal-gray
    document.getElementById("groupSideButton").style.backgroundColor = tile_pink; 
}

function lofiTheme(){
    const back_blue = '#89cfef';
    const back_mint = '#d0f0c0';
    const friend_purple = '#E5DAFB';
    const tile_white = '#F5F5F5';
    const text_black = '#221B1B';

    // change background of profile page to gradient of red to black
    document.body.style.backgroundImage = 'linear-gradient('+back_mint+','+back_blue +')';

    // change background of friend side bar metal-gray, text to ______
    document.getElementById("friendbar").style.backgroundColor = friend_purple;
    document.getElementById("follwingfriendtitle").style.color = '#191414';

    // change each friend tile to soft red 
    for(let i=0; document.getElementsByClassName("tile is-child notification")[i]; i++){
        document.getElementsByClassName("tile is-child notification")[i].style.backgroundColor = tile_white;
        document.getElementsByClassName("friendname")[i].style.color = text_black;
        document.getElementsByClassName("friendtext")[i].style.color = text_black;
    }

    // change each profile and bio tile to metal-gray
    for(let i=0; document.getElementsByClassName("tile is-child box")[i]; i++){
        document.getElementsByClassName("tile is-child box")[i].style.backgroundColor = friend_purple;
    }
    // change side group button to metal-gray
    document.getElementById("groupSideButton").style.backgroundColor = friend_purple; 
}