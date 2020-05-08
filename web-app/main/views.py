from flask import render_template, request, send_file
from main import app

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        result = request.form
        return send_file("static/routes_img.png", mimetype='image/png')
    
    return render_template('hello.html')