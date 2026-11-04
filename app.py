import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Yüklenen uygulamaların saklanacağı ana dizin
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'canlify_deployments')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ana Panel Arayüzü (HTML)
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canlify Pro • Bağımsız PWA Dağıtım Motoru</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: #111827;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --border: rgba(255, 255, 255, 0.08);
            --font: 'Plus Jakarta Sans', sans-serif;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg);
            color: var(--text-main);
            font-family: var(--font);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2.5rem 1rem;
        }
        header { text-align: center; margin-bottom: 2rem; }
        .brand { font-size: 2.2rem; font-weight: 700; color: var(--text-main); }
        .brand span { color: var(--accent-blue); }
        .subtitle { font-size: 0.9rem; color: var(--text-sub); margin-top: 6px; }
        .container {
            width: 100%;
            max-width: 800px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 25px 50px rgba(0,0,0,0.6);
            margin-bottom: 2rem;
        }
        .upload-form {
            border: 2px dashed rgba(56, 189, 248, 0.3);
            border-radius: 14px;
            padding: 2rem;
            text-align: center;
            background: rgba(56, 189, 248, 0.02);
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-form:hover { border-color: var(--accent-blue); background: rgba(56, 189, 248, 0.05); }
        input[type="file"] { margin: 1rem 0; color: var(--text-sub); }
        .btn-upload {
            width: 100%;
            background: linear-gradient(135deg, var(--accent-blue), #0284c7);
            color: #000;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-upload:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4); }
        .app-list { margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1.5rem; }
        .app-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .app-info div { font-weight: 600; font-size: 1rem; color: var(--text-main); }
        .app-link { font-size: 0.85rem; color: var(--accent-blue); text-decoration: none; margin-top: 4px; display: inline-block; }
        .app-link:hover { text-decoration: underline; }
        .btn-action {
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            font-size: 0.85rem;
            margin-left: 8px;
        }
        .btn-visit { background: var(--accent-green); color: #052e16; }
        .btn-del { background: var(--accent-red); color: #fff; display: inline-block; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <header>
        <div class="brand">⚡ Canlify <span>Pro Engine</span></div>
        <div class="subtitle">Sınırsız, Bağımsız ve Yerel PWA Dağıtım Altyapısı</div>
    </header>

    <div class="container">
        <form class="upload-form" action="/upload" method="POST" enctype="multipart/form-data">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">🚀</div>
            <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 10px;">PWA / HTML Uygulamanı Yükle</div>
            <input type="file" name="app_file" accept=".html,.htm" required><br>
            <button type="submit" class="btn-upload">Canlify'da Canlıya Al</button>
        </form>

        <div class="app-list">
            <div style="font-size: 0.95rem; color: var(--text-sub); margin-bottom: 1rem;">Yayındaki Uygulamalarım ({{ apps|length }})</div>
            {% if apps %}
                {% for app in apps %}
                <div class="app-item">
                    <div class="app-info">
                        <div>📦 {{ app.name }}</div>
                        <a href="/app/{{ app.slug }}/" target="_blank" class="app-link">🔗 /app/{{ app.slug }}/</a>
                    </div>
                    <div>
                        <a href="/app/{{ app.slug }}/" target="_blank" class="btn-action btn-visit">Aç / Çalıştır</a>
                        <form action="/delete/{{ app.slug }}" method="POST" style="display:inline;">
                            <button type="submit" class="btn-action btn-del">Kaldır</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align: center; color: var(--text-sub); font-size: 0.9rem; padding: 1rem;">Henüz yüklenmiş bir uygulama bulunmuyor.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    apps = []
    if os.path.exists(UPLOAD_FOLDER):
        for folder_name in os.listdir(UPLOAD_FOLDER):
            folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
            if os.path.isdir(folder_path):
                apps.append({'name': folder_name, 'slug': folder_name})
    return render_template_string(HOME_TEMPLATE, apps=apps)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # 1. Kullanıcı tarayıcıdan /upload adresine doğrudan (GET) girdiyse ana sayfaya at
    if request.method == 'GET':
        return redirect(url_for('index'))

    # 2. POST İŞLEMLERİ (Dosya Yükleme)
    file = request.files.get('file')
    
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        app_name = os.path.splitext(filename)[0]

        # Her uygulama için özel klasör açıyoruz
        app_dir = os.path.join(UPLOAD_FOLDER, app_name)
        os.makedirs(app_dir, exist_ok=True)

        # Dosyayı her zaman index.html olarak kaydediyoruz
        file.save(os.path.join(app_dir, 'index.html'))

    # 3. Yükleme tamamlandıktan sonra KESİNLİKLE ana sayfaya yönlendir (Çökmeden kurtaran kısım)
    return redirect(url_for('index'))


@app.route('/app/<app_slug>/', defaults={'path': ''})
@app.route('/app/<app_slug>/<path:path>')
def serve_app(app_slug, path):
    app_dir = os.path.join(UPLOAD_FOLDER, app_slug)
    if not os.path.exists(app_dir):
        abort(404)
    if path == "":
        path = "index.html"
    return send_from_directory(app_dir, path)

@app.route('/delete/<app_slug>', methods=['POST'])
def delete_app(app_slug):
    app_dir = os.path.join(UPLOAD_FOLDER, app_slug)
    if os.path.exists(app_dir):
        for f in os.listdir(app_dir):
            os.remove(os.path.join(app_dir, f))
        os.rmdir(app_dir)
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("⚡ Canlify Pro Engine Başlatıldı: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
