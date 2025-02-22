$(document).ready(function () {



    // Display Speak Message
    eel.expose(DisplayMassage)
    function DisplayMassage(massage) {
        // console.log("DisplayMessage called with:", message);
        $(".siri-massage li:first").text(massage);
        $('.siri-massage').textillate('start');

    }

    //Display the hood after the siriwave
    eel.expose(ShowHood)
    function ShowHood() {
        // console.log("showHood called");
        $("#Ovel").attr("hidden",false);
        $("#SiriWave").attr("hidden",true);
        }

    eel.expose(senderText)
    function senderText(massage){
        var chatbox = document.getElementById("chat-canvas-body");
        if (massage.trim() != ""){
            chatbox.innerHTML += `<div class="row justify-content-end mb-4">
                <div class="width-size">
                <div class="sender_massage">${massage}</div>
            </div>`;

        //Scroll to bottom of the chat box
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(massage){
        var chatbox = document.getElementById("chat-canvas-body");
        if (massage.trim() != ""){
            chatbox.innerHTML += `<div class="row justify-content-start mb-4">
                <div class="width-size">
                <div class="receiver_massage">${massage}</div>
            </div>`;

        //Scroll to bottom of the chat box
        chatbox.scrollTop = chatbox.scrollHeight;

            }
        }
    
        // Navigation
        document.getElementById("waveLink").addEventListener("click", function(event) {
            event.preventDefault();
            document.getElementById("SiriWave").hidden = false;
            document.getElementById("Ovel").hidden = true;
        });
    
        document.getElementById("homeNav").addEventListener("click", function(event) {
            event.preventDefault();
            document.getElementById("Ovel").hidden = false;
            document.getElementById("SiriWave").hidden = true;
        });
});