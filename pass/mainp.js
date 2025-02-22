const passwordInput = document.getElementById('password-input');
const submitBtn = document.getElementById('submit-btn');
const resultDiv = document.getElementById('result');
const segmentsContainer = document.querySelector('.segments-container');

let password = 'Jarvis'; // your password
let segmentCount = password.length;
let currentSegment = 0;

// create segments
for (let i = 0; i < segmentCount; i++) {
  const segment = document.createElement('div');
  segment.className ='segment';
  segment.style.top = `${i * 20}px`;
  segment.style.left = `${i * 20}px`;
  segmentsContainer.appendChild(segment);
}

// event handling
passwordInput.addEventListener('input', (e) => {
  const inputVal = e.target.value;
  if (inputVal === password) {
    // correct password
    resultDiv.textContent = 'Password correct!';
    // light up all segments
    segmentsContainer.querySelectorAll('.segment').forEach((segment) => {
      segment.classList.add('active');
    });
  } else {
    // incorrect password
    resultDiv.textContent = 'Wrong password!';
    // reset segments
    segmentsContainer.querySelectorAll('.segment').forEach((segment) => {
      segment.classList.remove('active');
    });
    currentSegment = 0;
  }
});

submitBtn.addEventListener('click', () => {
  const inputVal = passwordInput.value;
  if (inputVal === password) {
    // correct password
    resultDiv.textContent = 'Password correct!';
    // light up all segments
    segmentsContainer.querySelectorAll('.segment').forEach((segment) => {
      segment.classList.add('active');
    });
  } else {
    // incorrect password
    resultDiv.textContent = 'Wrong password!';
    // reset segments
    segmentsContainer.querySelectorAll('.segment').forEach((segment) => {
      segment.classList.remove('active');
    });
    currentSegment = 0;
  }
});