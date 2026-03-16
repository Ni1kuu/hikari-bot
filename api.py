from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/r34/<tag>")
def r34(tag):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={tag}"
    
    response = requests.get(url)
    data = response.json()

    images = []

    for post in data:
        img = post.get("file_url")
        if img:
            images.append(img)

    return jsonify(images)

@app.route("/")
def home():
    return "API online"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)