#labelling.py
 
from flask import Flask, render_template
import glob
from time import time

app = Flask(__name__)

@app.route("/")
def index():
     
    # 画像ファイルパスを取得
    img_path = glob.glob("static/daikiti/*")
    return render_template('index.html', img=img_path[int(time()) % 9])
        
if __name__ == "__main__":
    app.debug = True
    app.run()

