window.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
  
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          video.srcObject = stream;
        })
        .catch((err) => {
          console.error("שגיאה בהפעלת מצלמה:", err);
          alert("לא ניתן להפעיל את המצלמה");
        });
    } else {
      alert("הדפדפן שלך לא תומך במצלמה");
    }
  });

  function speakText() {
    const msg = document.getElementById("message").innerText;
    const utterance = new SpeechSynthesisUtterance(msg);
    utterance.lang = "en-US";
    speechSynthesis.speak(utterance);
  }

//   function startCapture() {
//     const timerElement = document.getElementById("timer");
//     let counter = 3;
  
//     timerElement.style.display = "block";
//     timerElement.innerText = counter;
  
//     const countdown = setInterval(() => {
//       counter--;
//       if (counter > 0) {
//         timerElement.innerText = counter;
//       } else {
//         clearInterval(countdown);
//         timerElement.style.display = "none";
  
//         // צילום מתוך הקנבס
//         const imageDataURL = canvas.toDataURL("image/png");
  
//         fetch("http://localhost:5000/upload", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ image: imageDataURL }),
//         })
//           .then(res => res.json())
//           .then(data => {
//             document.getElementById("message").innerText = data.message || "Image sent.";
//           })
//           .catch(err => {
//             console.error("Error sending image:", err);
//             document.getElementById("message").innerText = "Error occurred.";
//           });
//       }
//     }, 1000);
//   }

//   function startCountdown() {
//     const timerElement = document.getElementById("timer");
//     let count = 3;
//     timerElement.style.display = "block";
//     timerElement.innerText = count;
  
//     const interval = setInterval(() => {
//       count--;
//       if (count === 0) {
//         clearInterval(interval);
//         timerElement.innerText = "";
//         timerElement.style.display = "none";
//         captureAndSendImage(); // לקרוא לפונקציה 2
//       } else {
//         timerElement.innerText = count;
//       }
//     }, 1000);
//   }

function startCountdown(event) {
    if (event) event.preventDefault(); // מונע רענון דף
  
    const timerElement = document.getElementById("timer");
    let count = 3;
    timerElement.style.display = "block";
    timerElement.innerText = count;
  
    const interval = setInterval(() => {
      count--;
      if (count === 0) {
        clearInterval(interval);
        timerElement.innerText = "";
        timerElement.style.display = "none";
        captureAndSendImage();
      } else {
        timerElement.innerText = count;
      }
    }, 1000);
  }
  

//   function captureAndSendImage() {
//     const video = document.getElementById("video");
  
//     const canvas = document.createElement("canvas");
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext("2d");
  
//     // הפוך למראה
//     ctx.translate(canvas.width, 0);
//     ctx.scale(-1, 1);
//     ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
//     const imageData = canvas.toDataURL("image/png");
  
//     fetch("http://localhost:5000/upload", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({ image: imageData }),
//     })
//       .then((res) => res.json())
//       .then((data) => {
//         console.log("✅ Image sent:", data);
//       })
//       .catch((err) => {
//         console.error("❌ Error sending image:", err);
//       });
//   }
  
  
function captureAndSendImage() {
    const video = document.getElementById("video");
    const messageDiv = document.getElementById("message"); // אלמנט הצגת ההודעה
  
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
  
    // הפוך למראה
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
    const imageData = canvas.toDataURL("image/png");
  
    fetch("http://localhost:5000/upload", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image: imageData }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("✅ Image sent:", data);
        if (data.message) {
          messageDiv.textContent = data.message;  // עדכון ההודעה בדף
        } else {
          messageDiv.textContent = "No message received from server.";
        }
      })
      .catch((err) => {
        console.error("❌ Error sending image:", err);
        messageDiv.textContent = "Error sending image to server.";
      });
  }
  