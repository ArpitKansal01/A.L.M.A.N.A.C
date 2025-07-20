const signUpButton = document.getElementById("signUp");
const signInButton = document.getElementById("signIn");
const container = document.getElementById("container");

signUpButton.addEventListener("click", () => {
  container.classList.add("right-panel-active");
});

signInButton.addEventListener("click", () => {
  container.classList.remove("right-panel-active");
});

function typeWriter(elementId, text, speed) {
  let i = 0;
  function typing() {
    if (i < text.length) {
      document.getElementById(elementId).innerHTML += text.charAt(i);
      i++;
      setTimeout(typing, speed);
    }
  }
  typing();
}

window.onload = function () {
  typeWriter("welcomeBack", "Welcome Back, Agent!", 120);
  typeWriter("joinUs", "Join the AI Revolution!", 120);
};

// Matrix Rain Effect
var c = document.getElementById("matrix");
var ctx = c.getContext("2d");

// fullscreen
c.height = window.innerHeight;
c.width = window.innerWidth;

var matrix = "01";
matrix = matrix.split("");

var font_size = 14;
var columns = c.width / font_size; //number of columns
var drops = [];
for (var x = 0; x < columns; x++) drops[x] = 1;

function draw() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
  ctx.fillRect(0, 0, c.width, c.height);
  ctx.fillStyle = "#00f0ff"; // neon color
  ctx.font = font_size + "px monospace";
  for (var i = 0; i < drops.length; i++) {
    var text = matrix[Math.floor(Math.random() * matrix.length)];
    ctx.fillText(text, i * font_size, drops[i] * font_size);
    if (drops[i] * font_size > c.height && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  }
}
setInterval(draw, 33);

document.getElementById("signUpForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch("/sign_up", {
    method: "POST",
    body: new URLSearchParams({
      name: name,
      email: email,
      password: password,
    }),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message);
        });
      }
      return response.json();
    })
    .then((data) => {
      alert(data.message);
      // Switch to sign-in panel
      document
        .getElementById("container")
        .classList.remove("right-panel-active");
    })
    .catch((error) => {
      alert(error.message);
    });
});

document.getElementById("signInForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const email = document.getElementById("signInEmail").value;
  const password = document.getElementById("signInPassword").value;
  const errorDiv = document.getElementById("signInError");

  fetch("/login", {
    method: "POST",
    body: new URLSearchParams({
      email: email,
      password: password,
    }),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message);
        });
      }
      return response.json();
    })
    .then((data) => {
      errorDiv.textContent = ""; // clear error
      // 👇 After successful login, start face scan
      startFaceScan(data.message);
    })
    .catch((error) => {
      errorDiv.textContent = error.message;
    });
});

// ✨ Add the new functions here

function startFaceScan() {
  // Create overlay div for scanning
  const overlay = document.createElement("div");
  overlay.id = "face-scan-overlay";
  overlay.style.position = "fixed";
  overlay.style.top = 0;
  overlay.style.left = 0;
  overlay.style.width = "100vw";
  overlay.style.height = "100vh";
  overlay.style.backgroundColor = "rgba(0, 0, 0, 0.85)";
  overlay.style.display = "flex";
  overlay.style.flexDirection = "column";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = 9999;

  // Title - Scanning message
  const title = document.createElement("h2");
  title.innerText = "Starting Face Scan...";
  title.style.color = "#00f0ff";
  title.style.marginBottom = "20px";
  overlay.appendChild(title);

  // Create a loading animation (rotating circle)
  const loader = document.createElement("div");
  loader.style.border = "5px solid #f3f3f3";
  loader.style.borderTop = "5px solid #00f0ff";
  loader.style.borderRadius = "50%";
  loader.style.width = "50px";
  loader.style.height = "50px";
  loader.style.animation = "spin 1s linear infinite";
  overlay.appendChild(loader);

  // Video element
  const video = document.createElement("video");
  video.id = "scanVideo";
  video.style.width = "320px";
  video.style.height = "240px";
  video.style.border = "2px solid #00f0ff";
  video.style.borderRadius = "10px";
  overlay.appendChild(video);

  document.body.appendChild(overlay);

  // Start video stream for face scan
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      video.play();

      setTimeout(() => {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const base64Image = canvas.toDataURL("image/jpeg");

        // Stop the camera
        stream.getTracks().forEach((track) => track.stop());

        // Remove overlay for face scan
        document.body.removeChild(overlay);

        // Send image to the server for face verification
        sendFaceImage(base64Image);
      }, 3000); // 3 seconds scanning
    })
    .catch((err) => {
      console.error("Camera access denied", err);
      alert("Camera access denied.");
      document.body.removeChild(overlay);
    });
}

function sendFaceImage(base64Image) {
  const formData = new FormData();
  formData.append("image_data", base64Image);

  fetch("/verify_face", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Show success message
        console.log(data.name);
        showSuccessMessage(data.name);
      } else {
        alert("Face verification failed! Please try again.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Show success message after successful login and face scan
function showSuccessMessage(name) {
  // Create success message modal
  const successOverlay = document.createElement("div");
  successOverlay.id = "success-overlay";
  successOverlay.style.position = "fixed";
  successOverlay.style.top = 0;
  successOverlay.style.left = 0;
  successOverlay.style.width = "100vw";
  successOverlay.style.height = "100vh";
  successOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
  successOverlay.style.display = "flex";
  successOverlay.style.flexDirection = "column";
  successOverlay.style.alignItems = "center";
  successOverlay.style.justifyContent = "center";
  successOverlay.style.zIndex = 9999;

  // Create a box for success message
  const successBox = document.createElement("div");
  successBox.style.backgroundColor = "rgba(36, 36, 38, 0.9)";
  successBox.style.padding = "40px 60px";
  successBox.style.borderRadius = "10px";
  successBox.style.boxShadow = "0 0 15px rgba(0, 0, 0, 0.2)";
  successBox.style.textAlign = "center";
  successOverlay.appendChild(successBox);

  // Success message
  const successMessage = document.createElement("h2");
  successMessage.innerText = "Login Successful! Welcome, " + name + "!";
  successMessage.style.color = "#ffffff";
  successMessage.style.marginBottom = "20px";
  successBox.appendChild(successMessage);

  // Create a confirmation button
  const okButton = document.createElement("button");
  okButton.innerText = "Proceed to Home";
  okButton.style.padding = "10px 20px";
  okButton.style.backgroundColor = "#ffffff";
  okButton.style.border = "none";
  okButton.style.borderRadius = "5px";
  okButton.style.cursor = "pointer";
  okButton.style.color = "#00f0ff";
  okButton.onclick = () => {
    // Redirect to dashboard or the next page
    fetch("/run_assistant", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data.message);
        // Optionally, redirect or show a notification
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };
  successBox.appendChild(okButton);

  document.body.appendChild(successOverlay);
}
