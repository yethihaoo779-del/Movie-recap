import os
import json
import urllib.request
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Myanmar Movie Recap AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; margin: 0; }
            .card { max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            textarea { width: 100%; height: 120px; margin: 10px 0; border-radius: 5px; padding: 10px; background: #2b2b2b; color: white; border: 1px solid #444; font-size: 14px; box-sizing: border-box; }
            button { background: #e50914; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; }
            button:hover { background: #b80710; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 Myanmar Movie Recap Generator</h2>
            <form action="/generate" method="post">
                <textarea name="story" placeholder="ရုပ်ရှင်ဇာတ်လမ်း အကျဉ်းချုပ် သို့မဟုတ် Recap လုပ်ချင်သည့် အကြောင်းအရာကို ဒီမှာ ရိုက်ထည့်ပါ..." required></textarea><br>
                <button type="submit">Recap ဖန်တီးမည်</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_recap(story: str = Form(...)):
    if not GEMINI_API_KEY:
        return "<h3 style='color:white; text-align:center;'>API Key မရှိသေးပါ။ Render Environment မှာ GEMINI_API_KEY ထည့်သွင်းပေးပါ။</h3>"

    try:
        # Gemini REST API သို့ တိုက်ရိုက် တောင်းဆိုခြင်း
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        prompt_text = f"ဒီရုပ်ရှင်ဇာတ်လမ်းကို စိတ်လှုပ်ရှားစရာ Movie Recap Voiceover ပုံစံဖြင့် မြန်မာဘာသာစကားဖြင့် အသေးစိတ် ပြန်လည်ပြောပြပေးပါ:\n\n{story}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            
            recap_text = res_json['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        recap_text = f"API မှ အချက်အလက် ယူ၍မရပါ: {str(e)}"

    json_safe_text = json.dumps(recap_text)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Myanmar Movie Recap Result</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; margin: 0; }}
            .card {{ max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
            .result {{ text-align: left; background: #2a2a2a; padding: 15px; border-radius: 5px; line-height: 1.8; margin-top: 15px; font-size: 15px; color: #fff; white-space: pre-line; }}
            .audio-btn {{ background: #28a745; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-top: 10px; font-weight: bold; width: 100%; }}
            a {{ color: #e50914; text-decoration: none; display: inline-block; margin-top: 20px; font-weight: bold; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 ထွက်ရှိလာသော Myanmar Recap</h2>
            
            <button class="audio-btn" onclick="speakText()">🔊 အသံဖြင့် နားထောင်မည်</button>

            <h3>📜 မြန်မာ စာတန်းထိုး စာသား:</h3>
            <div class="result">{recap_text}</div>

            <a href="/">⬅ နောက်တစ်ခု ပြန်လုပ်မည်</a>
        </div>

        <script>
            function speakText() {{
                var text = {json_safe_text};
                var msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'my';
                window.speechSynthesis.speak(msg);
            }}
        </script>
    </body>
    </html>
    """
