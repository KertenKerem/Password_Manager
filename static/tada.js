{/*Script For Hide / Show Password */}
function pass_to_text(pid){
    var x = document.getElementById(pid);
    if (x.type === "password"){
        x.type = "text";
    }else{
        x.type = "password";
    }
}