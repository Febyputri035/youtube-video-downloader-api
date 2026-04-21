from flask import Flask, request, jsonify, render_template_string
from pytubefix import YouTube
import re, os

app = Flask(__name__)

# --- DASHBOARD DENGAN CODE SNIPPETS ALA RAPIDAPI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>YT API - Developer Dashboard</title>
    <style>
        body { font-family: 'Inter', -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .card { background: #1e293b; border-radius: 12px; padding: 25px; margin-bottom: 20px; border: 1px solid #334155; }
        h1 { color: #ef4444; margin-top: 0; }
        input, select { background: #0f172a; border: 1px solid #475569; color: white; padding: 12px; border-radius: 6px; width: 100%; margin: 10px 0; }
        button { background: #ef4444; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; }
        button:hover { background: #dc2626; }
        
        /* Snippets Styles */
        .snippet-box { background: #000; padding: 15px; border-radius: 8px; position: relative; margin-top: 10px; overflow-x: auto; }
        .lang-tab { display: inline-block; padding: 5px 15px; background: #334155; border-radius: 5px 5px 0 0; font-size: 12px; font-weight: bold; }
        pre { margin: 0; font-family: 'Consolas', monospace; color: #38bdf8; font-size: 13px; }
        .comment { color: #64748b; }
        .string { color: #facc15; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 YouTube Downloader API</h1>
        
        <div class="card">
            <h3>Try the API</h3>
            <input type="text" id="url" placeholder="https://www.youtube.com/watch?v=...">
            <select id="res">
                <option value="720p">720p (High)</option>
                <option value="360p">360p (Low)</option>
            </select>
            <button onclick="download()">Execute Download</button>
            <p id="status" style="margin-top:15px; font-weight:bold;"></p>
        </div>

        <div class="card">
            <h3>Code Snippets (Client SDKs)</h3>
            
            <div class="lang-tab">JavaScript (Fetch)</div>
            <div class="snippet-box">
<pre>
fetch(<span class="string">"http://127.0.0.1:5000/download/720p"</span>, {
  method: <span class="string">"POST"</span>,
  headers: { <span class="string">"Content-Type"</span>: <span class="string">"application/json"</span> },
  body: JSON.stringify({ url: <span class="string">"LINK_YOUTUBE"</span> })
})
.then(response => response.json())
.then(data => console.log(data));
</pre>
            </div>

            <div class="lang-tab" style="margin-top:20px;">Python (Requests)</div>
            <div class="snippet-box">
<pre>
import requests

url = <span class="string">"http://127.0.0.1:5000/download/720p"</span>
payload = { <span class="string">"url"</span>: <span class="string">"LINK_YOUTUBE"</span> }

response = requests.post(url, json=payload)
print(response.json())
</pre>
            </div>

            <div class="lang-tab" style="margin-top:20px;">PowerShell</div>
            <div class="snippet-box">
<pre>
<span class="comment"># Client Request</span>
$body = @{ url = <span class="string">"LINK_YOUTUBE"</span> } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri <span class="string">"http://127.0.0.1:5000/download/720p"</span> -Body $body -ContentType <span class="string">"application/json"</span>
</pre>
            </div>
        </div>
    </div>

    <script>
        async function download() {
            const url = document.getElementById('url').value;
            const res = document.getElementById('res').value;
            const status = document.getElementById('status');
            if(!url) { status.innerText = "Masukkan URL!"; return; }
            status.style.color = "#fbbf24";
            status.innerText = "⏳ Processing video...";
            
            try {
                const response = await fetch('/download/' + res, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                if(response.ok) {
                    status.style.color = "#4ade80";
                    status.innerText = "✅ " + data.message;
                } else {
                    status.style.color = "#f87171";
                    status.innerText = "❌ " + data.error;
                }
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

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url): return jsonify({"error": "Link tidak valid"}), 400
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            if not os.path.exists("./downloads"): os.makedirs("./downloads")
            stream.download(output_path="./downloads")
            return jsonify({"message": f"Berhasil! Video '{yt.title}' tersimpan di folder /downloads"}), 200
        return jsonify({"error": f"Resolusi {resolution} tidak tersedia untuk video ini."}), 404
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
