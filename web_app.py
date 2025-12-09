import os
import json
import uuid
from flask import Flask, request, render_template_string, send_file, jsonify
from dotenv import load_dotenv
from downloader import download_media

load_dotenv()

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Media Downloader</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
      color: #e0e0e0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .container {
      width: 100%;
      max-width: 650px;
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
    }

    .logo {
      font-size: 48px;
      margin-bottom: 16px;
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
    }

    h1 {
      font-size: 36px;
      font-weight: 700;
      background: linear-gradient(135deg, #00d4ff 0%, #7b68ee 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 10px;
    }

    .subtitle {
      color: #a0a0a0;
      font-size: 14px;
      font-weight: 500;
      letter-spacing: 0.5px;
    }

    .card {
      background: linear-gradient(135deg, rgba(30, 30, 50, 0.8) 0%, rgba(50, 50, 80, 0.6) 100%);
      border: 1px solid rgba(100, 150, 255, 0.2);
      border-radius: 20px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
    }

    label {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #00d4ff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .icon {
      font-size: 18px;
    }

    input[type="text"],
    select {
      background: rgba(20, 20, 35, 0.8);
      border: 1.5px solid rgba(100, 150, 255, 0.3);
      color: #e0e0e0;
      padding: 14px 18px;
      border-radius: 12px;
      font-size: 15px;
      transition: all 0.3s ease;
      font-family: inherit;
    }

    input[type="text"]::placeholder,
    select {
      color: #808080;
    }

    input[type="text"]:focus,
    select:focus {
      outline: none;
      border-color: rgba(0, 212, 255, 0.8);
      background: rgba(20, 20, 35, 1);
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }

    select {
      cursor: pointer;
      appearance: none;
      padding-right: 40px;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2300d4ff' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 16px center;
      padding-right: 44px;
    }

    .button-group {
      display: flex;
      gap: 12px;
      margin-top: 10px;
    }

    button {
      flex: 1;
      background: linear-gradient(135deg, #00d4ff 0%, #7b68ee 100%);
      color: #fff;
      border: none;
      padding: 16px 24px;
      border-radius: 12px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      text-transform: uppercase;
      letter-spacing: 1px;
      box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
      position: relative;
      overflow: hidden;
    }

    button::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.2);
      transition: left 0.5s ease;
      z-index: 0;
    }

    button:hover::before {
      left: 100%;
    }

    button:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 40px rgba(0, 212, 255, 0.5);
    }

    button:active {
      transform: translateY(-1px);
    }

    button span {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    #result {
      margin-top: 24px;
      padding: 18px 20px;
      border-radius: 12px;
      font-size: 15px;
      line-height: 1.6;
      min-height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      opacity: 0;
      transition: all 0.3s ease;
      pointer-events: none;
    }

    #result.loading {
      background: rgba(0, 212, 255, 0.1);
      border: 1px solid rgba(0, 212, 255, 0.3);
      color: #00d4ff;
      opacity: 1;
      pointer-events: auto;
      animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 0.7; }
      50% { opacity: 1; }
    }

    #result.success {
      background: rgba(76, 175, 80, 0.1);
      border: 1px solid rgba(76, 175, 80, 0.3);
      color: #4caf50;
      opacity: 1;
      pointer-events: auto;
    }

    #result.error {
      background: rgba(244, 67, 54, 0.1);
      border: 1px solid rgba(244, 67, 54, 0.3);
      color: #ff6b6b;
      opacity: 1;
      pointer-events: auto;
    }

    #result a {
      color: #00d4ff;
      text-decoration: none;
      font-weight: 600;
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid rgba(0, 212, 255, 0.5);
      transition: all 0.3s ease;
      display: inline-block;
      margin-top: 12px;
    }

    #result a:hover {
      background: rgba(0, 212, 255, 0.1);
      border-color: #00d4ff;
    }

    .loading-spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(0, 212, 255, 0.3);
      border-top: 2px solid #00d4ff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .helper-text {
      color: #808080;
      font-size: 12px;
      margin-top: 6px;
      font-style: italic;
    }

    @media (max-width: 600px) {
      h1 {
        font-size: 28px;
      }

      .card {
        padding: 24px;
      }

      button {
        padding: 12px 20px;
        font-size: 14px;
      }
    }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">⬇️</div>
    <h1>Media Downloader</h1>
    <p class="subtitle">Download from 1000+ platforms instantly</p>
  </div>

  <div class="card">
    <form method="post" action="/start" id="dlForm">
      <div class="form-group">
        <label for="url"><span class="icon">🔗</span>Media URL</label>
        <input 
          id="url"
          name="url" 
          type="text" 
          placeholder="https://youtube.com/watch?v=... or any supported platform"
          required
        >
        <div class="helper-text">Paste a link from YouTube, TikTok, Instagram, Pinterest, SoundCloud, Spotify, and more</div>
      </div>

      <div class="form-group">
        <label for="platform"><span class="icon">🎯</span>Platform</label>
        <select id="platform" name="platform">
          <option value="auto">🤖 Auto-detect</option>
          <option value="youtube">▶️ YouTube</option>
          <option value="tiktok">🎵 TikTok</option>
          <option value="instagram">📸 Instagram</option>
          <option value="vk">🇷🇺 VK</option>
          <option value="soundcloud">☁️ SoundCloud</option>
          <option value="spotify">🎧 Spotify</option>
          <option value="pinterest">📌 Pinterest</option>
          <option value="other">🌐 Other</option>
        </select>
      </div>

      <div class="form-group">
        <label for="kind"><span class="icon">🎬</span>Download Type</label>
        <select id="kind" name="kind">
          <option value="video">🎥 Video (best quality)</option>
          <option value="audio">🎵 Audio (MP3)</option>
        </select>
      </div>

      <div class="button-group">
        <button type="submit">
          <span>⬇️ Download</span>
        </button>
      </div>
    </form>

    <div id="result"></div>
  </div>
</div>

<script>
const form = document.getElementById('dlForm');
const resultDiv = document.getElementById('result');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const url = document.getElementById('url').value.trim();
  if (!url) {
    showError('Please enter a valid URL');
    return;
  }

  resultDiv.className = 'loading';
  resultDiv.innerHTML = '<div class="loading-spinner"></div> Downloading... Please wait';

  const formData = new FormData(form);
  
  fetch(form.action, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      return response.text().then(text => Promise.reject(text));
    }
    
    // Extract filename from Content-Disposition header or use default
    const disposition = response.headers.get('Content-Disposition');
    let filename = 'download';
    if (disposition) {
      const matches = disposition.match(/filename="?(.+?)"?$/);
      if (matches) filename = matches[1];
    }
    
    return response.blob().then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      showSuccess('File downloaded successfully!');
    });
  })
  .catch(error => {
    console.error('Download error:', error);
    showError(error || 'Download failed. Please check the URL and try again.');
  });
});

function showError(msg) {
  resultDiv.className = 'error';
  resultDiv.innerHTML = `⚠️ ${msg}`;
}

function showSuccess(msg) {
  resultDiv.className = 'success';
  resultDiv.innerHTML = `✅ ${msg}`;
  setTimeout(() => {
    resultDiv.className = '';
    resultDiv.innerHTML = '';
  }, 5000);
}
</script>
</body>
</html>
'''
@app.route('/')
def index():
                return render_template_string(TEMPLATE)


@app.route('/start', methods=['POST'])
def start():
        # synchronous download: performs download immediately and returns file
        url = request.form.get('url', '').strip()
        kind = request.form.get('kind', 'video')
        platform = request.form.get('platform', 'auto')
        if not url:
                return 'Provide URL', 400

        # call downloader synchronously; disable redis writes for this immediate flow
        try:
                path = download_media(url, kind=kind, job_id=None, cookies_text=None, max_filesize=None, use_redis=False)
        except Exception as e:
                error_msg = f'Error during download: {str(e)}'
                print(f'[ERROR] {error_msg}', flush=True)  # log to container stdout
                return error_msg, 500

        if not os.path.exists(path):
                error_msg = f'Download succeeded but file missing at {path}'
                print(f'[ERROR] {error_msg}', flush=True)
                return error_msg, 500
        return send_file(path, as_attachment=True)


@app.route('/demo', methods=['GET', 'POST'])
def demo():
        # Synchronous demo download (no Redis/RQ). Good for local testing without Redis.
        from yt_dlp import YoutubeDL
        if request.method == 'POST':
                url = request.form.get('url')
                kind = request.form.get('kind', 'video')
                if not url:
                        return 'url required', 400
                outtmpl = os.path.join(os.path.dirname(__file__), 'downloads', '%(title)s.%(ext)s')
                os.makedirs(os.path.dirname(outtmpl), exist_ok=True)
                opts = {'outtmpl': outtmpl, 'noplaylist': True}
                if kind == 'video':
                        opts.update({'format': 'bestvideo+bestaudio/best'})
                else:
                        opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]})
                try:
                        with YoutubeDL(opts) as ydl:
                                info = ydl.extract_info(url, download=True)
                                filename = ydl.prepare_filename(info)
                        return send_file(filename, as_attachment=True)
                except Exception as e:
                        return f'Error: {e}', 500
        return '''
        <form method="post">
          URL: <input name="url" size="80"><br>
          Type: <select name="kind"><option value="video">video</option><option value="audio">audio</option></select><br>
          <button type="submit">Download (sync demo)</button>
        </form>
        '''


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=True)
