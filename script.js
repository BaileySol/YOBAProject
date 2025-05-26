// Init: מחכה לטעינת תוכן הדף ואז מאתחל את כל המרכיבים
window.addEventListener("DOMContentLoaded", initPage);

function initPage() {
  const poseName = getPoseFromUrl();
  startSpeechRecognitionLoop();
  fetchPoseInstructions(poseName);
  initializeCamera();
}

// מחלץ מה-URL את הפרמטר pose
function getPoseFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('pose');
}

// מאתחל את המצלמה ומציג את הזרם בווידאו
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

// שולח בקשה לשרת לקבלת הוראות לתנוחה
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

// מעדכן את אלמנט ההודעה בטקסט הנתון
function updateMessage(message) {
  const messageElement = document.getElementById("message");
  messageElement.innerText = message;
}

// מפעיל את ההקראה של רשימת הוראות אחת אחרי השנייה
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

// יוצר מופע של SpeechSynthesisUtterance עם פרמטרים מוגדרים
function createUtterance(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  utterance.rate = 0.85;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  return utterance;
}

// מפעיל לולאת זיהוי דיבור שמאזינה באופן רציף
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

// מפעיל טיימר של 3 שניות ולבסוף מצלם תמונה
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

// לוכד תמונה מהוידאו ושולח אותה לשרת
function captureAndSendImage() {
  const videoElement = document.getElementById("video");
  const canvas = document.createElement("canvas");
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const context = canvas.getContext("2d");

  // מבצע השתקפות אופקית (מראה)
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


// ביטול הקראת הסינטזה בעת יציאת המשתמש מהדף
window.addEventListener("beforeunload", () => {
  speechSynthesis.cancel();
});