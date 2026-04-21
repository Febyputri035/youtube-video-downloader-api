from flask import Flask, request, jsonify, render_template_string
from pytubefix import YouTube
import re
import os

app = Flask(__name__)

# --- TEMPLATE HTML UNTUK HALAMAN DOCS ---
HTML_DOCS = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader API Docs</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; color: #333; padding: 20px; }
        .card { background: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        code { background: #eee; padding: 2px 5px; border-radius: 4px; color: #d63384; }
        .method { font-weight: bold; color: #007bff; }
        .endpoint { font-weight: bold; font-size: 1.1em; }
        h1 { color: #cc0000; }
        .try-it { background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; }
    </style>
</head>
<body>
    <h1>📺 YouTube API Downloader Docs</h1>
    <p>Selamat datang! API ini sedang berjalan. Kamu bisa menggunakan endpoint di bawah ini:</p>

    <div class="card">
        <span class="method">POST</span> <span class="endpoint">/video_info</span>
        <p>Mendapatkan informasi detail tentang video YouTube.</p>
        <code>Body: {"url": "LINK_YOUTUBE"}</code>
    </div>

    <div class="card">
        <span class="method">POST</span> <span class="endpoint">/available_resolutions</span>
        <p>Melihat daftar resolusi yang bisa didownload.</p>
        <code>Body: {"url": "LINK_YOUTUBE"}</code>
    </div>

    <div class="card">
        <span class="method">POST</span> <span class="endpoint">/download/&lt;resolution&gt;</span>
        <p>Mendownload video dengan resolusi spesifik (contoh: <code>/download/720p</code>).</p>
        <code>Body: {"url": "LINK_YOUTUBE"}</code>
    </div>

    <hr>
    <div class="try-it">
        <h3>💡 Tips Cepat:</h3>
        <p>Karena API ini menggunakan <b>POST</b>, kamu tidak bisa langsung klik link di atas. 
        Gunakan aplikasi seperti <b>Postman</b> atau perintah PowerShell yang tadi kita pelajari.</p>
    </div>
</body>
</html>
"""

def download_video(url, resolution):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            out_dir = f"./downloads/{url.split('v=')[1].split('&')[0]}"
            os.makedirs(out_dir, exist_ok=True)
            stream.download(output_path=out_dir)
            return True, None
        else:
            return False, "Video with the specified resolution not found."
    except Exception as e:
        return False, str(e)

def get_video_info(url):
    try:
        yt = YouTube(url)
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

# --- ENDPOINT BARU: HALAMAN DOCS ---
@app.route('/')
def index():
    return render_template_string(HTML_DOCS)

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400
    
    success, error_message = download_video(url, resolution)
    if success:
        return jsonify({"message": f"Resolution {resolution} downloaded."}), 200
    return jsonify({"error": error_message}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400
    
    info, error = get_video_info(url)
    return jsonify(info) if info else (jsonify({"error": error}), 500)

@app.route('/available_resolutions', methods=['POST'])
def available_resolutions():
    data = request.get_json()
    url = data.get('url')
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400
    
    try:
        yt = YouTube(url)
        res = sorted(list(set([s.resolution for s in yt.streams.filter(progressive=True) if s.resolution])))
        return jsonify({"available_resolutions": res}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
