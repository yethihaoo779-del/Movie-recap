import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Movie Recap Generator</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #1a1a1a; color: white; }
            h1 { color: #e50914; }
            .container { max-width: 500px; margin: auto; background: #222; padding: 20px; border-radius: 10px; }
            input, button { width: 90%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
            button { background-color: #e50914; color: white; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Movie Recap Generator</h1>
            <p>Welcome to your AI Movie Recap Service!</p>
            <input type="text" placeholder="Enter Movie Name or Video URL...">
            <button onclick="alert('Processing your recap...')">Generate Recap</button>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
