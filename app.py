import os
import re
import json
import urllib.request
import urllib.error
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

def get_youtube_id(url):
    pattern = r'(?:v=|\/live\/|\/embed\/|\/shorts\/|\/v\/|youtu\.be\/|\/e\/)([^"&?\/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def extract_text_from_link(url):
    try:
        yt_id = get_youtube_id(url)
        if yt_id:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(yt_id, languages=['my', 'en'])
                text = " ".join([item['text'] for item in transcript_list])
                return text if text else "YouTube စာတန်းထိုး ရှာမတွေ့ပါ။"
            except Exception:
                return "YouTube ဗီဒီယိုမှ စာတန်းထိုး ဖတ်ယူ၍ မရပါ။ (Subtitle ပိတ်ထားခြင်း ဖြစ်နိုင်ပါတယ်)"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        page_text = " ".join([p.get_text() for p in paragraphs])
        return page_text[:4000] if page_text else "Website မှ စာသားများ ဖတ်ယူ၍ မရပါ။"
    except Exception as e:
        return f"Link မှ စာသားယူရာတွင် Error တက်သွားသည်: {str(e)}"

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
            textarea, input, select { width: 100%; margin: 8px 0; border-radius: 5px; padding: 10px; background: #2b2b2b; color: white; border: 1px solid #444; font-size: 14px; box-sizing: border-box; }
            textarea { height: 100px; }
            button { background: #e50914; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }
            button:hover { background: #b80710; }
            label { display: block; text-align: left; margin-top: 10px; color: #bbb; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 Movie Recap Generator v2</h2>
            <form action="/generate" method="post">
                <label>1. Google Gemini API Key ထည့်ပါ:</label>
                <input type="text" name="api_key" placeholder="Gemini API Key ထည့်ပါ" required>
                
                <label>2. ဇာတ်လမ်းထည့်သွင်းမည့် နည်းလမ်းရွေးပါ:</label>
                <select name="input_type" onchange="toggleInput(this.value)">
                    <option value="text">ဇာတ်လမ်း စာသားတိုက်ရိုက်ရိုက်ထည့်မည်</option>
                    <option value="link">Website / YouTube Link ထည့်မည်</option>
                </select>

                <div id="textGroup">
                    <textarea name="story" placeholder="ဇာတ်လမ်းအကျဉ်းချုပ် ရိုက်ထည့်ပါ..."></textarea>
                </div>

                <div id="linkGroup" style="display:none;">
                    <input type="url" name="link_url" placeholder="https://youtube.com/watch?... သို့မဟုတ် Website Link">
                </div>

                <button type="submit">Recap ဖန်တီးမည်</button>
            </form>
        </div>

        <script>
            function toggleInput(val) {
                if(val === 'text') {
                    document.getElementById('textGroup').style.display = 'block';
                    document.getElementById('linkGroup').style.display = 'none';
                } else {
                    document.getElementById('textGroup').style.display = 'none';
                    document.getElementById('linkGroup').style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_recap(
    api_key: str = Form(...),
    input_type: str = Form(...),
    story: str = Form(""),
    link_url: str = Form("")
):
    api_key = api_key.strip()
    source_content = ""

    if input_type == "link" and link_url:
        source_content = extract_text_from_link(link_url.strip())
    else:
        source_content = story.strip()

    if not source_content:
        return "<h3>ကျေးဇူးပြု၍ ဇာတ်လမ်း သို့မဟုတ် Link ထည့်သွင်းပေးပါ။</h3><a href='/'>ပြန်သွားမည်</a>"

    # Gemini 2.0 Flash Model Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    prompt_text = f"ဒီအကြောင်းအရာ/ဇာတ်လမ်းကို စိတ်လှုပ်ရှားစရာ Movie Recap Voiceover ပုံစံဖြင့် မြန်မာဘာသာစကားဖြင့် အသေးစိတ် ပြန်လည်ပြောပြပေးပါ:\n\n{source_content}"

    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    recap_text = ""
    error_msg = ""

    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            recap_text = res_json['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        error_msg = f"HTTP Error {e.code}: {e.reason}<br><small style='color:#ccc;'>{error_body}</small>"
    except Exception as e:
        error_msg = f"Error: {str(e)}"

    json_safe_text = json.dumps(recap_text)

    if error_msg:
        content_html = f"<div style='color: #ff5252; font-weight: bold; margin-top: 15px;'>{error_msg}</div>"
    else:
        content_html = f"""
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
                var msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'my';
                window.speechSynthesis.speak(msg);
            }}
        </script>
    </body>
    </html>
    """
