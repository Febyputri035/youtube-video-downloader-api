from flask import Flask, request, jsonify, render_template_string
from pytubefix import YouTube
import re, os

app = Flask(__name__)

# --- INI HALAMAN DASHBOARD & DOCS (OTOMATIS MUNCUL DI BROWSER) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>YouTube Downloader API - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 700px; margin: 50px auto; background: #f4f7f6; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #ff0000; text-align: center; }
        .section { margin-bottom: 25px; padding: 15px; border: 1px solid #eee; border-radius: 8px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { background: #ff0000; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; }
        button:hover { background: #cc0000; }
        code { background: #272822; color: #f8f8f2; padding: 10px; display: block; border-radius: 5px; font-size: 0.9em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 YT Downloader Dashboard</h1>
        
        <div class="section">
            <h3>1. Download Langsung (Mudah)</h3>
            <p>Masukkan link YouTube & resolusi (contoh: 720p), lalu klik download.</p>
            <input type="text" id="url" placeholder="https://www.youtube.com/watch?v=...">
            <input type="text" id="res" placeholder="720p" value="720p">
            <button onclick="download()">Download Video</button>
            <p id="status"></p>
        </div>

        <div class="section">
            <h3>2. Dokumentasi API (Endpoint)</h3>
            <p>Jika ingin pakai PowerShell/Code lain:</p>
            <ul>
                <li><code>POST /video_info</code> - Cek info video</li>
                <li><code>POST /download/&lt;res&gt;</code> - Proses download</li>
            </ul>
        </div>
    </div>

    <script>
        async function download() {
            const url = document.getElementById('url').value;
            const res = document.getElementById('res').value;
            const status = document.getElementById('status');
            status.innerText = "Sedang memproses...";
            
            try {
                const response = await fetch('/download/' + res, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                status.innerText = data.message || data.error;
            } catch (e) {
                status.innerText = "Error: " + e;
            }
        }
    </script>
</body>
</html>
"""

def is_valid_youtube_url(url):
    return re.match(r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+", url) is not None

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url): return jsonify({"error": "Link tidak valid"}), 400
    try:
        yt = YouTube(url)
        return jsonify({"title": yt.title, "author": yt.author, "length": yt.length}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url): return jsonify({"error": "Link tidak valid"}), 400
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            os.makedirs("./downloads", exist_ok=True)
            stream.download(output_path="./downloads")
            return jsonify({"message": f"Berhasil! Video {yt.title} tersimpan di folder /downloads"}), 200
        return jsonify({"error": "Resolusi tidak ditemukan"}), 404
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
