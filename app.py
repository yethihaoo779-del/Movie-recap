import os
import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="my">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Myanmar Movie Recap Generator</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; margin: 0; }
            .card { max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
            textarea, input { width: 100%; margin: 8px 0; border-radius: 5px; padding: 10px; background: #2b2b2b; color: white; border: 1px solid #444; font-size: 14px; box-sizing: border-box; }
            textarea { height: 120px; }
            button { background: #e50914; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }
            button:hover { background: #b80710; }
            label { display: block; text-align: left; margin-top: 10px; color: #bbb; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 Movie Recap Generator</h2>
            <form action="/generate" method="post">
                <label>1. Google Gemini API Key ထည့်ပါ:</label>
                <input type="text" name="api_key" placeholder="Gemini API Key ထည့်ပါ" required>
                
                <label>2. ဇာတ်လမ်း အကြောင်းအရာ ရိုက်ထည့်ပါ:</label>
                <textarea name="story" placeholder="ဇာတ်လမ်းအကျဉ်းချုပ် ရိုက်ထည့်ပါ..." required></textarea>

                <button type="submit">Recap ဖန်တီးမည်</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_recap(
    api_key: str = Form(...),
    story: str = Form("")
):
    api_key = api_key.strip()
    source_content = story.strip()

    if not source_content:
        return "<h3>ကျေးဇူးပြု၍ ဇာတ်လမ်း ထည့်သွင်းပေးပါ။</h3><a href='/'>ပြန်သွားမည်</a>"

    prompt_text = f"""
    မင်းက ကျွမ်းကျင်တဲ့ မြန်မာ Movie Recap Voiceover ရေးသားသူဖြစ်ပါတယ်။ 
    အောက်ပါ ဇာတ်လမ်းကို စိတ်လှုပ်ရှားစရာ ရုပ်ရှင်အသံသွင်း စာသားအဖြစ် ရေးပေးပါ။

    [အရေးကြီးသော စည်းမျဉ်းများ]
    ၁။ စာသားအားလုံးကို **မြန်မာဘာသာစကား (Myanmar Language)** ဖြင့်သာ မဖြစ်မနေ ရေးရမည်။
    ၂။ အင်္ဂလိပ်စာလုံး လုံးဝ မသုံးရပါ။ မြန်မာလိုပဲ သန့်သန့်ရေးပေးပါ။

    ဇာတ်လမ်းအကြောင်းအရာ:
    {source_content}
    """

    recap_text = ""
    used_model = ""
    error_logs = []

    try:
        genai.configure(api_key=api_key)
        
        # API Key ဖြင့် အသုံးပြုနိုင်သော Model များကို ရှာဖွေခြင်း
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Gemma မော်ဒယ်များကို ပယ်ထုတ်ပြီး Gemini သီးသန့်ရွေးမည်
                if 'gemma' not in m.name.lower():
                    available_models.append(m.name)
        
        # Gemini မော်ဒယ်များကို အစဉ်လိုက် စမ်းသပ်မည်
        for model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt_text)
                if response.text:
                    recap_text = response.text
                    used_model = model_name
                    break
            except Exception as inner_e:
                error_logs.append(f"{model_name}: {str(inner_e)}")

    except Exception as e:
        error_logs.append(f"SDK Error: {str(e)}")

    json_safe_text = json.dumps(recap_text if recap_text else "")

    if not recap_text:
        content_html = f"""
        <div style='color: #ff5252; font-weight: bold; margin-top: 15px;'>
            API Key စစ်ဆေးပါ သို့မဟုတ် မော်ဒယ်များ ခေါ်ယူ၍ မရပါ: <br>
            <small style='color:#ccc;'>{ '<br>'.join(error_logs) if error_logs else 'API Key မှားယွင်းနေခြင်း သို့မဟုတ် မော်ဒယ်မရှိခြင်း ဖြစ်နိုင်ပါသည်။' }</small>
        </div>
        """
    else:
        content_html = f"""
        <p style="color: #4caf50; font-size: 13px; font-weight: bold;">(အဆင်ပြေစွာ သုံးသွားသော Model: {used_model})</p>
        <button class="audio-btn" onclick="speakText()">🔊 အသံဖြင့် နားထောင်မည်</button>
        <h3>📜 ထွက်ရှိလာသော Recap စာသား:</h3>
        <div class="result">{recap_text}</div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="my">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Myanmar Movie Recap Result</title>
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
            <h2>🎬 Myanmar Recap ရလဒ်</h2>
            {content_html}
            <a href="/">⬅ နောက်တစ်ခု ပြန်လုပ်မည်</a>
        </div>
        <script>
            function speakText() {{
                var text = {json_safe_text};
                if (!text) return;

                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance(text);
                    msg.rate = 0.9;
                    window.speechSynthesis.speak(msg);
                }} else {{
                    alert("သင့် Browser မှ အသံထွက်စနစ်ကို ထောက်ပံ့မှုမရှိပါ။");
                }}
            }}
        </script>
    </body>
    </html>
    """
