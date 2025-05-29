// Init: Waits for the page content to load and then initializes all components
window.addEventListener("DOMContentLoaded", initPage);

function initPage() {
  const poseName = getPoseFromUrl();
  startSpeechRecognitionLoop();
  fetchPoseInstructions(poseName);
  initializeCamera();
}

// Extracts the pose parameter from the URL
function getPoseFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('pose');
}

// Initializes the camera and displays the video stream
function initializeCamera() {
  const videoElement = document.getElementById("video");
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        videoElement.srcObject = stream;
      })
      .catch((error) => {
        console.error("Error launching camera:", error);
        alert("The camera cannot be turned on. Please check your permissions.");
      });
  } else {
    alert("Your browser does not support the camera. Please try a different browser.");
  }
}

// Sends a request to the server for pose instructions
function fetchPoseInstructions(poseName) {
  fetch(`http://localhost:5000/instructions/${poseName}`)
    .then(res => res.json())
    .then(data => {
      if (data.instructions) {
        updateMessage(data.instructions.join(" "));
        speakInstructions(data.instructions);
      } else {
        updateMessage("No instructions received.");
      }
    })
    .catch(error => {
      console.error("Error fetching instructions:", error);
      updateMessage("Failed to fetch instructions.");
    });
}

// Updates the message element with the given text
function updateMessage(message) {
  const messageElement = document.getElementById("message");
  messageElement.innerText = message;
}

// Starts reading a list of instructions one after the other
function speakInstructions(instructions) {
  let currentInstructionIndex = 0;

  function speakNextInstruction() {
    if (currentInstructionIndex >= instructions.length) return;

    const utterance = createUtterance(instructions[currentInstructionIndex]);
    utterance.onend = function () {
      currentInstructionIndex++;
      setTimeout(speakNextInstruction, 750);
    };

    speechSynthesis.speak(utterance);
  }

  speakNextInstruction();
}

// Creates an instance of SpeechSynthesisUtterance with defined parameters
function createUtterance(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.85;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  return utterance;
}

// Starts a speech recognition loop that listens continuously
function startSpeechRecognitionLoop() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript.trim().toLowerCase();
    console.log("Recognized speech:", transcript);
    if (transcript === "yes") {
      initiateCountdown();
    }
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    updateMessage(`Error: ${event.error}`);
    if (event.error !== "not-allowed") {
      setTimeout(() => recognition.start(), 1000);
    }
  };

  recognition.onend = function () {
    console.log("Recognition ended, restarting...");
    recognition.start();
  };

  recognition.start();
}

// Starts a 3 second timer and finally takes a picture
function initiateCountdown(event) {
  if (event) event.preventDefault();

  const timerElement = document.getElementById("timer");
  let count = 3;
  timerElement.style.display = "block";
  timerElement.innerText = count;

  const countdownInterval = setInterval(() => {
    count--;
    if (count === 0) {
      clearInterval(countdownInterval);
      timerElement.innerText = "";
      timerElement.style.display = "none";
      captureAndSendImage();
    } else {
      timerElement.innerText = count;
    }
  }, 1000);
}

// Captures an image from the video and sends it to the server
function captureAndSendImage() {
  const videoElement = document.getElementById("video");
  const canvas = document.createElement("canvas");
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const context = canvas.getContext("2d");

// Performs horizontal reflection (mirror)
  context.translate(canvas.width, 0);
  context.scale(-1, 1);
  context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL("image/png");

  fetch("http://localhost:5000/upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData })
  })
    .then(response => response.json())
    .then(data => {
      console.log("Image sent:", data);
      if (data.message) {
        alert(data.message);
      } else {
        alert("No message received from server.");
      }
    })
    .catch(error => {
      console.error("Error sending image:", error);
      alert("Error sending image to server.");
    });
}

function speakText() {
  const msg = document.getElementById("message").innerText;
  const utterance = new SpeechSynthesisUtterance(msg);
  utterance.lang = "en-US";
  speechSynthesis.speak(utterance);
}


// Cancel the synthesis reading when the user leaves the page
window.addEventListener("beforeunload", () => {
  speechSynthesis.cancel();
});
