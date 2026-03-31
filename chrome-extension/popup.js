const DEFAULT_API_URL = 'https://my-container-qhx9vl5u-3000.serverless.fptcloud.com';

let apiUrl = localStorage.getItem('apiUrl') || DEFAULT_API_URL;

document.getElementById('apiUrl').value = apiUrl;

document.getElementById('analyzeBtn').addEventListener('click', analyze);
document.getElementById('settingsToggle').addEventListener('click', toggleSettings);

document.getElementById('apiUrl').addEventListener('change', (e) => {
  apiUrl = e.target.value.trim() || DEFAULT_API_URL;
  localStorage.setItem('apiUrl', apiUrl);
});

document.getElementById('emailText').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    analyze();
  }
});

function toggleSettings() {
  document.getElementById('settingsPanel').classList.toggle('show');
}

async function scanCurrentEmail() {
  const btn = document.getElementById('analyzeBtn');
  const errorDiv = document.getElementById('error');
  const resultDiv = document.getElementById('result');

  errorDiv.classList.remove('show');
  resultDiv.classList.remove('show', 'phishing', 'benign');
  document.getElementById('emailText').value = '';

  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span>Scanning email...';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const response = await chrome.tabs.sendMessage(tab.id, { action: 'getEmailContent' });
    
    if (!response || !response.body) {
      throw new Error('No email detected. Please open an email first.');
    }

    const fullText = response.subject ? `${response.subject}\n\n${response.body}` : response.body;
    document.getElementById('emailText').value = fullText;
    
    await analyze();

  } catch (error) {
    console.error('Error:', error);
    if (error.message.includes('No email detected')) {
      showError(error.message);
    } else if (error.message.includes('Cannot connect')) {
      showError(error.message);
    } else {
      showError('Cannot scan this page. Try copying the email manually.');
    }
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze';
  }
}

async function analyze() {
  const text = document.getElementById('emailText').value.trim();
  const btn = document.getElementById('analyzeBtn');
  const resultDiv = document.getElementById('result');
  const errorDiv = document.getElementById('error');

  errorDiv.classList.remove('show');
  resultDiv.classList.remove('show', 'phishing', 'benign');

  if (!text) {
    showError('Please enter text to analyze');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span>Analyzing...';

  try {
    const response = await fetch(`${apiUrl}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    showResult(data);

  } catch (error) {
    console.error('Error:', error);
    if (error.message.includes('Failed to fetch')) {
      showError(`Cannot connect to API at ${apiUrl}. Please check if the server is running.`);
    } else {
      showError(error.message);
    }
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze';
  }
}

function showResult(data) {
  const resultDiv = document.getElementById('result');
  const labelSpan = document.getElementById('resultLabel');
  const confidenceText = document.getElementById('confidenceText');
  const confidenceBar = document.getElementById('confidenceBar');

  const isPhishing = data.is_phishing || data.label === 'PHISHING';
  const confidence = data.confidence * 100;

  resultDiv.classList.add('show');
  resultDiv.classList.add(isPhishing ? 'phishing' : 'benign');

  labelSpan.textContent = isPhishing ? '⚠️ PHISHING' : '✓ BENIGN';
  confidenceText.textContent = `${confidence.toFixed(1)}%`;
  confidenceBar.style.width = `${confidence}%`;
}

function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.classList.add('show');
}

// Check if on email page and add scan button
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0]) {
    const url = tabs[0].url || '';
    const isEmailPage = url.includes('mail.google.com') || 
                        url.includes('outlook.live.com') || 
                        url.includes('mail.yahoo.com');
    
    if (isEmailPage) {
      const container = document.querySelector('.container');
      const scanBtn = document.createElement('button');
      scanBtn.id = 'scanEmailBtn';
      scanBtn.className = 'btn btn-primary';
      scanBtn.style.marginTop = '8px';
      scanBtn.textContent = '📧 Scan Current Email';
      scanBtn.addEventListener('click', scanCurrentEmail);
      container.insertBefore(scanBtn, container.children[1]);
    }
  }
});
