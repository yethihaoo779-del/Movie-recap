import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from gtts import gTTS
import google.generativeai as genai

app = FastAPI()

# Render Environment Variable မှ API Key ကို ရယူခြင်း
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
            textarea { width: 90%; height: 120px; margin: 10px 0; border-radius: 5px; padding: 10px; background: #2b2b2b; color: white; border: 1px solid #444; font-size: 14px; }
            button { background: #e50914; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 95%; }
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
    try:
        if not GEMINI_API_KEY:
            return "<h3>API Key မရှိသေးပါ။ Render Environment မှာ GEMINI_API_KEY ထည့်သွင်းပေးပါ။</h3>"

        # 1. Gemini AI ဖြင့် မြန်မာလို Movie Recap စာသားထုတ်ခြင်း
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"ဒီရုပ်ရှင်ဇာတ်လမ်းကို စိတ်လှုပ်ရှားစရာ Movie Recap Voiceover ပုံစံဖြင့် မြန်မာဘာသာစကားဖြင့် အသေးစိတ် ပြန်လည်ပြောပြပေးပါ:\n\n{story}"
        response = model.generate_content(prompt)
        recap_text = response.text

        # 2. စာသားကို မြန်မာအသံအဖြစ် ပြောင်းလဲခြင်း (gTTS)
        tts = gTTS(text=recap_text, lang='my')
        audio_path = "recap_audio.mp3"
        tts.save(audio_path)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Myanmar Movie Recap Result</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: sans-serif; text-align: center; padding: 20px; background: #121212; color: white; margin: 0; }}
                .card {{ max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
                .result {{ text-align: left; background: #2a2a2a; padding: 15px; border-radius: 5px; white-space: pre-line; line-height: 1.8; margin-top: 15px; font-size: 15px; }}
                a {{ color: #e50914; text-decoration: none; display: inline-block; margin-top: 20px; font-weight: bold; font-size: 16px; }}
                audio {{ width: 100%; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🎬 ထွက်ရှိလာသော Myanmar Recap</h2>
                
                <h3>🔊 မြန်မာလို အသံနားထောင်ရန်:</h3>
                <audio controls autoplay>
                    <source src="/audio" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>

                <h3>📜 မြန်မာ စာတန်းထိုး စာသား:</h3>
                <div class="result">{recap_text}</div>

                <a href="/">⬅ နောက်တစ်ခု ပြန်လုပ်မည်</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<div style='color: white; padding: 20px;'><h3>အမှားအယွင်း ဖြစ်ပေါ်ခဲ့ပါသည်:</h3><p>{str(e)}</p><a href='/' style='color: #e50914;'>ပြန်သွားမည်</a></div>"

@app.get("/audio")
async def get_audio():
    return FileResponse("recap_audio.mp3", media_type="audio/mpeg")
