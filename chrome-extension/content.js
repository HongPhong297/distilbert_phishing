// Content script để extract email content từ Gmail/Outlook
// Sử dụng: Click extension icon khi đang xem email

(function() {
  function getEmailContent() {
    // Gmail
    if (window.location.hostname.includes('mail.google.com')) {
      return extractGmail();
    }
    // Outlook
    if (window.location.hostname.includes('outlook.live.com')) {
      return extractOutlook();
    }
    // Yahoo
    if (window.location.hostname.includes('mail.yahoo.com')) {
      return extractYahoo();
    }
    return null;
  }

  function extractGmail() {
    // Lấy nội dung email đang xem
    const emailBody = document.querySelector('.a3s.aiL');
    const subject = document.querySelector('h2.hP')?.textContent;
    
    if (!emailBody) return null;
    
    return {
      subject: subject || '',
      body: emailBody.textContent,
      html: emailBody.innerHTML
    };
  }

  function extractOutlook() {
    const emailBody = document.querySelector('[role="main"] .outlook-body');
    const subject = document.querySelector('[role="heading"]')?.textContent;
    
    if (!emailBody) return null;
    
    return {
      subject: subject || '',
      body: emailBody.textContent,
      html: emailBody.innerHTML
    };
  }

  function extractYahoo() {
    const emailBody = document.querySelector('.message-body');
    const subject = document.querySelector('subject')?.textContent;
    
    if (!emailBody) return null;
    
    return {
      subject: subject || '',
      body: emailBody.textContent,
      html: emailBody.innerHTML
    };
  }

  // Lắng nghe message từ popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getEmailContent') {
      const content = getEmailContent();
      sendResponse(content);
    }
    return true;
  });
})();
