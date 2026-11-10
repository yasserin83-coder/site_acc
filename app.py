from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import json, os, random, time

app = FastAPI()

# ==================== ⚙️ إعدادات ====================
ADMIN_PASSWORD = "admin123"  # غير كلمة سر لوحة التحكم
STOCK_FILE = "accounts_stock.json"  # الملف الذي سيتم حفظ الحسابات فيه
IP_FILE = "ips_record.json" # لحفظ من أخذ حساباً لمنع التكرار

# دوال التعامل مع الملفات
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f: return json.load(f)
        except: pass
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f)

# ==================== 🎨 الواجهة الأمامية (تصميم غامض ومتحرك) ====================
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Secret CPM Vault</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        :root { 
            --primary: #8a2be2; /* بنفسجي غامض */
            --glow: rgba(138, 43, 226, 0.4); 
            --bg: #020204;
        }
        * { box-sizing: border-box; font-family: 'Outfit', sans-serif; margin: 0; padding: 0; }
        
        body {
            background-color: var(--bg); color: #fff; height: 100vh;
            display: flex; justify-content: center; align-items: center; overflow: hidden; position: relative;
        }

        /* تأثير الخلفية الغامضة المتحركة (جزيئات ونجوم) */
        .stars { position: absolute; width: 100%; height: 100%; z-index: 0; overflow: hidden; }
        .star {
            position: absolute; background: white; border-radius: 50%;
            opacity: 0.5; animation: twinkle infinite alternate;
        }
        @keyframes twinkle { from { opacity: 0.1; transform: scale(0.8); } to { opacity: 0.8; transform: scale(1.2); box-shadow: 0 0 10px white; } }

        /* الكارت الزجاجي الغامض */
        .vault-card {
            position: relative; z-index: 10; width: 100%; max-width: 400px;
            background: rgba(10, 10, 15, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 30px;
            padding: 40px 30px; text-align: center;
            box-shadow: 0 0 50px rgba(138, 43, 226, 0.15), inset 0 0 20px rgba(138, 43, 226, 0.1);
            animation: floatCard 6s ease-in-out infinite;
        }
        @keyframes floatCard { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }

        /* الدائرة المتوهجة */
        .orb {
            width: 100px; height: 100px; margin: 0 auto 25px auto; border-radius: 50%;
            background: radial-gradient(circle, rgba(138, 43, 226, 0.8) 0%, transparent 70%);
            border: 2px solid var(--primary); display: flex; justify-content: center; align-items: center;
            font-size: 40px; box-shadow: 0 0 30px var(--glow);
            animation: pulseOrb 2s infinite alternate;
        }
        @keyframes pulseOrb { from { box-shadow: 0 0 20px var(--glow); } to { box-shadow: 0 0 60px var(--glow), 0 0 100px var(--primary); transform: scale(1.05); } }

        h1 { font-size: 28px; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px; color: #fff; text-shadow: 0 0 10px var(--glow); }
        p { font-size: 14px; color: #888; margin-bottom: 30px; line-height: 1.6; }

        /* الزر الغامض القوي */
        .btn {
            width: 100%; padding: 18px; border: none; border-radius: 16px;
            background: linear-gradient(45deg, #4b0082, #8a2be2); color: #fff;
            font-size: 18px; font-weight: 800; cursor: pointer;
            box-shadow: 0 0 20px var(--glow); transition: 0.3s; position: relative; overflow: hidden;
        }
        .btn:hover { transform: scale(1.02); box-shadow: 0 0 40px var(--glow); }
        .btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: 0.5s; }
        .btn:hover::before { left: 100%; }

        /* شاشة الحساب */
        .account-box { display: none; text-align: right; margin-top: 20px; animation: slideUp 0.5s ease; }
        .data-row {
            background: rgba(0,0,0,0.5); padding: 15px; border-radius: 12px; margin-bottom: 10px;
            border: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;
        }
        .data-row span { font-family: monospace; font-size: 15px; color: #00ffcc; direction: ltr; }
        .copy-btn { background: rgba(255,255,255,0.1); border: none; color: #fff; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-family: inherit; }
        .copy-btn:hover { background: var(--primary); }

        /* رسالة الثقة */
        .trust-msg {
            margin-top: 20px; padding: 15px; background: rgba(255, 215, 0, 0.1); border: 1px dashed #ffd700;
            border-radius: 12px; color: #ffd700; font-size: 14px; font-weight: 600; display: none; animation: blink 2s infinite;
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
        
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="stars" id="stars"></div>

    <div class="vault-card">
        <div class="orb">🔐</div>
        <h1>CPM SECRET VAULT</h1>
        <p>خزنة الحسابات السرية. اضغط للحصول على حسابك العشوائي قبل نفاد الكمية.</p>
        
        <button class="btn" id="main-btn" onclick="getAccount()">احصل على حساب الآن 🚀</button>

        <div id="loader" class="hidden" style="margin-top: 20px;">
            <div class="orb" style="width:50px; height:50px; font-size:20px; animation: spin 2s linear infinite;">⏳</div>
        </div>

        <div class="account-box" id="account-box">
            <div class="data-row">
                <div><b>Email:</b><br><span id="res-email"></span></div>
                <button class="copy-btn" onclick="copy('res-email')">نسخ</button>
            </div>
            <div class="data-row">
                <div><b>Password:</b><br><span id="res-pass"></span></div>
                <button class="copy-btn" onclick="copy('res-pass')">نسخ</button>
            </div>
        </div>

        <div class="trust-msg" id="trust-msg">
            ⚠️ لا تنسَ ترك "إثبات" أو "كلمة ثقة" في التعليقات لدعمنا! 🙏
        </div>
    </div>

    <script>
        // إنشاء نجوم متحركة في الخلفية
        const starsContainer = document.getElementById('stars');
        for(let i=0; i<100; i++) {
            let star = document.createElement('div');
            star.className = 'star';
            star.style.width = Math.random() * 3 + 'px';
            star.style.height = star.style.width;
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDuration = (Math.random() * 3 + 1) + 's';
            star.style.animationDelay = Math.random() * 2 + 's';
            starsContainer.appendChild(star);
        }

        async function getAccount() {
            document.getElementById('main-btn').classList.add('hidden');
            document.getElementById('loader').classList.remove('hidden');
            document.getElementById('account-box').classList.add('hidden');
            document.getElementById('trust-msg').classList.add('hidden');

            try {
                const res = await fetch('/api/get_account', { method: 'POST' });
                const data = await res.json();
                
                document.getElementById('loader').classList.add('hidden');
                
                if (data.success) {
                    document.getElementById('account-box').classList.remove('hidden');
                    document.getElementById('trust-msg').classList.remove('hidden');
                    document.getElementById('res-email').innerText = data.email;
                    document.getElementById('res-pass').innerText = data.password;
                } else {
                    // في حال نفاذ المخزون
                    document.getElementById('main-btn').classList.remove('hidden');
                    document.getElementById('main-btn').innerText = "نفذت الكمية! ❌";
                    document.getElementById('main-btn').style.background = "#333";
                    document.getElementById('main-btn').style.boxShadow = "none";
                }
            } catch(e) {
                alert("حدث خطأ في الاتصال.");
                document.getElementById('main-btn').classList.remove('hidden');
            }
        }

        function copy(id) {
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text);
            alert("تم النسخ بنجاح!");
        }
    </script>
</body>
</html>
"""

# ==================== 👑 لوحة الأدمن لرفع المخزون ====================
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>Admin - Stock</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { background: #020204; color: #fff; font-family: 'Outfit', sans-serif; padding: 40px; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .box { width: 100%; max-width: 500px; background: rgba(15, 15, 20, 0.9); padding: 40px; border-radius: 24px; border: 1px solid #8a2be2; box-shadow: 0 0 30px rgba(138,43,226,0.2); }
        h1 { text-align: center; margin-bottom: 30px; color: #8a2be2; font-size: 24px; font-weight: 800; }
        label { font-size: 14px; color: #aaa; margin-bottom: 10px; display: block; }
        input[type="file"] { width: 100%; padding: 15px; margin-bottom: 20px; background: #000; border: 1px dashed #555; border-radius: 12px; color: #fff; cursor: pointer; }
        button { width: 100%; padding: 16px; background: linear-gradient(45deg, #4b0082, #8a2be2); color: #fff; font-weight: 800; border: none; border-radius: 12px; cursor: pointer; font-size: 16px; transition: 0.3s; }
        button:hover { box-shadow: 0 0 20px rgba(138,43,226,0.5); transform: translateY(-2px); }
        .stats { text-align: center; margin-top: 20px; font-size: 18px; color: #00ffcc; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>مخزون الحسابات</h1>
        <form action="/admin/upload" method="post" enctype="multipart/form-data">
            <label>ارفع ملف نصي (txt) يحتوي على الحسابات (email:password) كل حساب في سطر:</label>
            <input type="file" name="file" accept=".txt" required>
            <button type="submit">تعبئة المخزون 🚀</button>
        </form>
        <div class="stats" id="stats">جاري حساب العدد...</div>
    </div>
    <script>
        fetch('/api/stock_count').then(r => r.json()).then(d => {
            document.getElementById('stats').innerText = "الحسابات المتوفرة حالياً: " + d.count;
        });
    </script>
</body>
</html>
"""

# ==================== 🛠️ مسارات الموقع (API) ====================
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_MAIN

@app.post("/api/get_account")
async def get_account(request: Request):
    # التحقق من الـ IP (اختياري: يمكنك إزالة هذا الجزء إذا كنت تريد السماح للشخص بسحب أكثر من حساب)
    client_ip = request.client.host
    ips = load_json(IP_FILE)
    now = time.time()

    # حماية: حساب واحد كل 12 ساعة لكل شخص (لمنع سحب كل المخزون في دقيقة)
    if client_ip in ips:
        time_passed = now - ips[client_ip]
        if time_passed < 43200: # 12 ساعة
            return {"success": False, "error": "لقد أخذت حساباً بالفعل اليوم. حاول غداً."}

    # سحب حساب من المخزون
    stock = load_json(STOCK_FILE)
    if not stock:
        return {"success": False, "error": "نفذت الكمية"}

    # اختيار حساب عشوائي وحذفه من المخزون
    acc = random.choice(stock)
    stock.remove(acc)
    save_json(STOCK_FILE, stock)

    # تسجيل الـ IP
    ips[client_ip] = now
    save_json(IP_FILE, ips)

    return {"success": True, "email": acc["email"], "password": acc["password"]}

@app.get("/api/stock_count")
async def stock_count():
    stock = load_json(STOCK_FILE)
    return {"count": len(stock)}

# ==================== 👑 مسارات الأدمن ====================
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(passkey: str = ""):
    if passkey != ADMIN_PASSWORD: return HTMLResponse("<h1 style='color:red;text-align:center;margin-top:50px;'>🚫 ممنوع</h1>", status_code=403)
    return ADMIN_HTML

@app.post("/admin/upload")
async def admin_upload(passkey: str = "", file: UploadFile = File(...)):
    if passkey != ADMIN_PASSWORD: raise HTTPException(status_code=403)
    
    content = await file.read()
    lines = content.decode("utf-8", errors="ignore").splitlines()
    
    stock = load_json(STOCK_FILE)
    added_count = 0
    
    for line in lines:
        if ":" in line:
            email, password = line.split(":", 1)
            stock.append({"email": email.strip(), "password": password.strip()})
            added_count += 1
            
    save_json(STOCK_FILE, stock)
    return HTMLResponse(f"<h1 style='color:#00ff00;text-align:center;margin-top:50px;font-family:sans-serif;'>✅ تم إضافة {added_count} حساب للمخزون بنجاح.</h1>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)