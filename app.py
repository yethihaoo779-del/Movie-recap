from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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
            .audio-btn { background: #28a745; margin-top: 15px; display: none; }
            .result { text-align: left; background: #2a2a2a; padding: 15px; border-radius: 5px; line-height: 1.8; margin-top: 15px; font-size: 15px; color: #fff; white-space: pre-line; display: none; }
            #loading { display: none; margin-top: 15px; color: #ffc107; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🎬 Myanmar Movie Recap Generator</h2>
            
            <input type="password" id="apiKey" placeholder="Google Gemini API Key ထည့်ပါ (AIzaSy...)" required>
            <textarea id="story" placeholder="ရုပ်ရှင်ဇာတ်လမ်း အကျဉ်းချုပ်ကို ဒီမှာ ရိုက်ထည့်ပါ..." required></textarea>
            
            <button onclick="generateRecap()">Recap ဖန်တီးမည်</button>

            <div id="loading">⏳ Gemini AI မှ Recap စာတန်းထိုး ဖန်တီးနေပါသည်။ ခဏစောင့်ပါ...</div>

            <button id="audioBtn" class="audio-btn" onclick="speakText()">🔊 အသံဖြင့် နားထောင်မည်</button>
            
            <div id="resultText" class="result"></div>
        </div>

        <script>
            let generatedText = "";

            async function generateRecap() {
                const apiKey = document.getElementById('apiKey').value.trim();
                const story = document.getElementById('story').value.trim();

                if (!apiKey) {
                    alert("ကျေးဇူးပြု၍ API Key ထည့်သွင်းပေးပါ!");
                    return;
                }
                if (!story) {
                    alert("ကျေးဇူးပြု၍ ဇာတ်လမ်းအကျဉ်း ရိုက်ထည့်ပေးပါ!");
                    return;
                }

                document.getElementById('loading').style.display = 'block';
                document.getElementById('resultText').style.display = 'none';
                document.getElementById('audioBtn').style.display = 'none';

                const prompt = "ဒီရုပ်ရှင်ဇာတ်လမ်းကို စိတ်လှုပ်ရှားစရာ Movie Recap Voiceover ပုံစံဖြင့် မြန်မာဘာသာစကားဖြင့် အသေးစိတ် ပြန်လည်ပြောပြပေးပါ:\n\n" + story;

                try {
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            contents: [{ parts: [{ text: prompt }] }]
                        })
                    });

                    const data = await response.json();
                    document.getElementById('loading').style.display = 'none';

                    if (data.candidates && data.candidates[0].content.parts[0].text) {
                        generatedText = data.candidates[0].content.parts[0].text;
                        document.getElementById('resultText').innerText = generatedText;
                        document.getElementById('resultText').style.display = 'block';
                        document.getElementById('audioBtn').style.display = 'block';
                    } else {
                        alert("API Error: အချက်အလက်ယူ၍ မရပါ။ API Key မှန်မမှန် ပြန်စစ်ပါ။");
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert("Error တက်သွားပါသည်: " + error.message);
                }
            }

            function speakText() {
                if (!generatedText) return;
                var msg = new SpeechSynthesisUtterance(generatedText);
                msg.lang = 'my';
                window.speechSynthesis.speak(msg);
            }
        </script>
    </body>
    </html>
    """
