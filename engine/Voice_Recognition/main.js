const recordButton = document.getElementById("record");
const trainButton = document.getElementById("train");
const authButton = document.getElementById("authenticate");
const statusText = document.getElementById("status");
const recordingIndicator = document.getElementById("recording-indicator"); // 🎤 Indicator
let audioData = [];

// 🎤 Show and Hide Recording Indicator
function showRecordingIndicator() {
    recordingIndicator.style.display = "block";
}

function hideRecordingIndicator() {
    recordingIndicator.style.display = "none";
}


async function saveModel() {
    const username = document.getElementById("username").value.trim();
    if (!username) {
        statusText.innerText = "Enter a username before saving!";
        return;
    }
    await userModel.save(`indexeddb://voice-auth-model-${username}`);
    statusText.innerText = `✅ Model saved for ${username}!`;
}

async function loadModel() {
    const username = document.getElementById("username").value.trim();
    if (!username) {
        statusText.innerText = "Enter a username before loading!";
        return;
    }
    try {
        userModel = await tf.loadLayersModel(`indexeddb://voice-auth-model-${username}`);
        statusText.innerText = `✅ Model loaded for ${username}!`;
    } catch (error) {
        console.warn("⚠️ No saved model found for this user.");
    }
}



async function recordVoice() {
    try {
        console.log("Starting recording...");
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        let chunks = [];

        showRecordingIndicator(); // 🎤 Show indicator when recording starts

        return new Promise((resolve, reject) => {
            mediaRecorder.ondataavailable = (event) => {
                console.log("Data chunk received:", event.data.size, "bytes");
                chunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                hideRecordingIndicator(); // 🎤 Hide indicator when recording stops
                console.log("Recording stopped, processing audio...");
                const audioBlob = new Blob(chunks, { type: "audio/wav" });
                console.log("Audio blob size:", audioBlob.size, "bytes");

                audioData = await extractMFCC(audioBlob);
                statusText.innerText = "Voice recorded successfully!";
                resolve(audioData);
            };

            mediaRecorder.onerror = (event) => {
                console.error("Recording error:", event.error);
                statusText.innerText = "Error during recording: " + event.error;
                hideRecordingIndicator(); // 🎤 Hide indicator if an error occurs
                reject(event.error);
            };

            mediaRecorder.start();
            console.log("MediaRecorder started");
            statusText.innerText = "Recording... Speak now!";
            
            setTimeout(() => {
                mediaRecorder.stop();
                console.log("MediaRecorder stopped");
            }, 5000); // Record for 5 seconds
        });
    } catch (error) {
        console.error("Error accessing microphone:", error);
        statusText.innerText = "Error: " + error.message;
    }
}

// 🎤 Extract Features (MFCC) with Fixes
async function extractMFCC(audioBlob) {
    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioContext = new AudioContext();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    return tf.tidy(() => {
        const waveform = tf.tensor1d(audioBuffer.getChannelData(0));
        const spectrogram = tf.signal.stft(waveform, 1024, 512);

        const realPart = tf.real(spectrogram);
        const imagPart = tf.imag(spectrogram);

        let featureVector = tf.concat([realPart, imagPart], 1).mean(1);

        const targetLength = 409;
        const currentLength = featureVector.shape[0];

        if (currentLength > targetLength) {
            featureVector = featureVector.slice(0, targetLength);
        } else if (currentLength < targetLength) {
            const padding = tf.zeros([targetLength - currentLength]);
            featureVector = featureVector.concat(padding);
        }

        return featureVector.dataSync();
    });
}

let userModel = null;

// 🎤 Train the Model
async function trainModel() {
    if (audioData.length === 0) {
        statusText.innerText = "Please record voice first!";
        return;
    }

    userModel = tf.sequential();
    userModel.add(tf.layers.dense({ units: 10, activation: "relu", inputShape: [audioData.length] }));
    userModel.add(tf.layers.dense({ units: 1, activation: "sigmoid" }));

    userModel.compile({ optimizer: "adam", loss: "binaryCrossentropy", metrics: ["accuracy"] });

    const xs = tf.tensor2d([audioData]);
    const ys = tf.tensor2d([[1]]); 

    await userModel.fit(xs, ys, { epochs: 50 });
    statusText.innerText = "Model trained successfully!";
}

// 🎤 Authenticate User
async function authenticateUser() {
    if (!userModel) {
        statusText.innerText = "Train the model first!";
        return;
    }

    statusText.innerText = "Recording for authentication...";
    const newAudioData = await recordVoice(); // Wait for recording to finish

    const xs = tf.tensor2d([newAudioData]);
    const prediction = userModel.predict(xs).dataSync()[0];

    if (prediction > 0.5) {
        statusText.innerText = "✅ Authentication Successful!";
    } else {
        statusText.innerText = "❌ Authentication Failed!";
    }
}

async function saveModel1() {
    if (!userModel) {
        statusText.innerText = "No trained model to save!";
        return;
    }
    await userModel.save('indexeddb://voice-auth-model');
    statusText.innerText = "✅ Model saved successfully!";
}

async function loadModel1() {
    try {
        userModel = await tf.loadLayersModel('indexeddb://voice-auth-model');
        statusText.innerText = "✅ Model loaded successfully!";
    } catch (error) {
        console.warn("⚠️ No saved model found. Train a model first!");
    }
}

// Load model on page load
window.onload = async () => {
    await loadModel();
};


// 🔹 Event Listeners
recordButton.addEventListener("click", recordVoice);
trainButton.addEventListener("click", trainModel);
authButton.addEventListener("click", authenticateUser);
saveModel.addEventListener("click", saveModel1);
loadModel.addEventListener("click", loadModel1);