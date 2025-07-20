$(document).ready(function () {
  $(".text").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  // Siri Wave
  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 900,
    height: 200,
    style: "ios9",
    amplitute: "650",
    speed: "0.40",
    autoStart: true,
  });

  // Siri message Animation
  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  // Mic Button event
  $("#MicBtn").click(function () {
    eel.playAssistantSound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
    eel.allcommand()();
  });

  function doc_keyUp(e) {
    // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

    if (e.key === "z" && e.metaKey) {
      eel.playAssistantSound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.allcommand()();
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);
});

// to play assisatnt
function PlayAssistant(message) {
  if (message != "") {
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
    eel.allcommand(message);
    $("#chatbox").val("");
    $("#MicBtn").attr("hidden", false);
    $("#SendBtn").attr("hidden", true);
  }
}

// toogle fucntion to hide and display mic and send button
function ShowHideButton(message) {
  if (message.length == 0) {
    $("#MicBtn").attr("hidden", false);
    $("#SendBtn").attr("hidden", true);
  } else {
    $("#MicBtn").attr("hidden", true);
    $("#SendBtn").attr("hidden", false);
  }
}

$("#chatbox").keyup(function () {
  let message = $("#chatbox").val();
  ShowHideButton(message);
});

// send button event handler
$("#SendBtn").click(function () {
  let message = $("#chatbox").val();
  PlayAssistant(message);
});

// enter press event handler on chat box
$("#chatbox").keypress(function (e) {
  key = e.which;
  if (key == 13) {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  }
});
