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
    cont="I can see"+context+"in the pictures, describe whats going on in one sentence? Keep it factual, dont use emotional langues, stay neutral."
    openai_url = 'https://api.openai.com/v1/completions'  # Use the appropriate OpenAI endpoint
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
    return response.json()['choices'][0]['text'] if response.ok else None



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    descriptions=''
    if 'files[]' not in request.files:
        return "No files part"

    files = request.files.getlist('files[]')
    for file in files:
        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            file.save(f"{app.config['UPLOAD_FOLDER']}/{file.filename}")
            descriptions+='  '
            descriptions+=classifyImage('uploads/'+file.filename)
    
    
    openai_response = generate_openai_response(descriptions)
    print(openai_response)

    return openai_response

if __name__ == '__main__':
    app.run(debug=True)
