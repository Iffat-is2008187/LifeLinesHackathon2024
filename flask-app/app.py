from flask import Flask, render_template, request
import requests
from classifier import classifyImage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['OPENAI_API_KEY'] = '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'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_openai_response(context):
    cont = "I can see" + context + "in the pictures, describe what's going on in one sentence? Keep it factual, don't use emotional language, stay neutral."
    openai_url = 'https://api.openai.com/v1/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {app.config["OPENAI_API_KEY"]}'
    }
    data = {
        'model': 'gpt-3.5-turbo-instruct',
        'prompt': cont,
        'max_tokens': 100
    }
    response = requests.post(openai_url, json=data, headers=headers)

    if response.ok:
        return response.json()['choices'][0]['text']
    else:
        print("OpenAI API Request Error:")
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        return None




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads', methods=['POST'])
def upload_file():
    descriptions = ''
    if 'files[]' not in request.files:
        return "No files part"

    files = request.files.getlist('files[]')
    for file in files:
        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            file.save(f"{app.config['UPLOAD_FOLDER']}/{file.filename}")
            descriptions += '  '
            descriptions += classifyImage('uploads/' + file.filename)
    print(descriptions)        
    openai_response = generate_openai_response(descriptions)
    return openai_response

if __name__ == '__main__':
    app.run(debug=True)