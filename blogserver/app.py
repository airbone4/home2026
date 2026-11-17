import os
from flask import Flask, render_template_string, request, redirect, url_for, abort
import markdown

app = Flask(__name__)
# 設定存放 MD 檔案的資料夾
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blogs')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制最大上傳 16MB

# 確保資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ─── HTML 範本 ───
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的 Markdown 部落格</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }
        header { border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        h1 a { text-decoration: none; color: #2c3e50; }
        .upload-box { background: #f9f9f9; padding: 15px; border: 1px dashed #ccc; border-radius: 6px; margin-bottom: 30px; }
        .post-list { list-style: none; padding: 0; }
        .post-item { padding: 10px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .post-date { color: #888; font-size: 0.9em; }
        .back-btn { display: inline-block; margin-bottom: 20px; text-decoration: none; color: #3498db; }
        article { background: #fff; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <header>
        <h1><a href="/">📝 朋友的分享空間</a></h1>
    </header>
    {% block content %}{% endblock %}
</body>
</html>
"""

INDEX_TEMPLATE = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <div class="upload-box">
        <h3>📤 上傳新的 Blog (.md)</h3>
        <form action="{{ url_for('upload_file') }}" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".md" required>
            <button type="submit">確認上傳</button>
        </form>
    </div>

    <h2>文章列表 (依最新時間排序)</h2>
    <ul class="post-list">
        {% for post in posts %}
        <li class="post-item">
            <a href="{{ url_for('view_post', filename=post.filename) }}">{{ post.title }}</a>
            <span class="post-date">{{ post.date }}</span>
        </li>
        {% else %}
        <li>目前還沒有任何文章，快上傳一篇吧！</li>
        {% endfor %}
    </ul>
""")

POST_TEMPLATE = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <a href="/" class="back-btn">⬅️ 回到列表</a>
    <article>
        {{ content | safe }}
    </article>
""")

# ─── 網頁路由 ───

# 1. 首頁：列出所有文章（按檔案最後修改時間由新到舊排序）
@app.route('/')
def index():
    posts = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for fname in os.listdir(app.config['UPLOAD_FOLDER']):
            if fname.endswith('.md'):
                fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                mtime = os.path.getmtime(fpath) # 取得最後修改時間
                import datetime
                date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                
                posts.append({
                    'filename': fname,
                    'title': fname[:-3], # 去除 .md 作為標題
                    'date': date_str,
                    'raw_time': mtime
                })
        # 根據時間排序 (最新在上)
        posts.sort(key=lambda x: x['raw_time'], reverse=True)
        
    return render_template_string(INDEX_TEMPLATE, posts=posts)

# 2. 上傳處理
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.md'):
        # 儲存檔案
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    return redirect(url_for('index'))

# 3. 文章內頁：將 MD 轉成 HTML 顯示
@app.route('/post/<filename>')
def view_post(filename):
    # 安全檢查，防止目錄穿越攻擊
    if '/' in filename or '\\' in filename:
        abort(400)
        
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(fpath):
        abort(404)
        
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
        # 轉換 Markdown 為 HTML，擴充支援表格與程式碼高亮
        html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
        
    return render_template_string(POST_TEMPLATE, content=html_content)

if __name__ == '__main__':
    # host='0.0.0.0' 代表允許區域網路內的所有裝置（如朋友的手機、電腦）連線
    app.run(host='0.0.0.0', port=5000, debug=True)