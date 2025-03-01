$(document).ready(function () {
    $('.text').textillate({
        loop: true,
        sync: true,
        in:{
            effect: "bounceIn",
        },
        out:{
            effect: "bounceOut",
        },

    })
    //Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
    });
    //Siri-massage-animation
    $('.siri-massage').textillate({
        loop: true,
        sync: true,
        in:{
            effect: "fadeInUp",
            sync: true,
        },
        out:{
            effect: "fadeOutUp",
            sync: true,
        },
    });

    //mic button click event
    $("#MicBtn").click(function (e) { 
        eel.playAssistanatSound()
        // the above line will play sound of start
        $("#Ovel").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()()
    });

    // Close button for SiriWave
    $("#closeSiriWave").click(function () {
        $("#Ovel").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    });
    
    //code of shortcut key
    function doc_keyUp(e) {
        // Check for both Command (Mac) and Ctrl (Windows) keys
        if (e.key.toLowerCase() === 'j' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault(); // Prevent default browser behavior
            eel.playAssistanatSound()
            $("#Ovel").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);    

// message taken from text area 
    function PlayAssistanat(massage){
        
        if (massage != ""){

            $("#Ovel").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(massage);
            $("#chatbox").val("")
            $("#MicBtn").attr("hidden", true);
            $("#SendBtn").attr("hidden", true);
        }
    }

    function ShowHideButton(massage){
        if(massage.length == 0){
            $("#MicBtn").attr("hidden", false);
            $("#SendBtn").attr("hidden", true);
        }
        else{
            $("#MicBtn").attr("hidden", true);
            $("#SendBtn").attr("hidden", false);
        }
    }

    $("#chatbox").keyup( function(){
    
        let massage = $("#chatbox").val();
        ShowHideButton(massage);
        
    });

    $("#SendBtn").click(function() {
        
        let massage = $("#chatbox").val();
        PlayAssistanat(massage);
    }); 

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let massage = $("#chatbox").val()
            PlayAssistanat(massage)
        }
    });




});