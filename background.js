// background.js - 隐形代理，浏览器最高权限运行
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'proxy') {
    fetch(request.url, {
      method: request.method || 'GET',
      headers: request.headers || {},
      body: request.body
    })
    .then(r => {
      const headers = {};
      r.headers.forEach((v, k) => headers[k] = v);
      return r.text().then(text => ({ body: text, headers, status: r.status }));
    })
    .then(data => sendResponse({ success: true, data }))
    .catch(err => sendResponse({ success: false, error: err.message }));

    return true; // 异步响应
  }
});