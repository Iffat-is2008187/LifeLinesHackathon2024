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
    openai_url = 'https://api.openai.com/v1/chat/completions'  # Use the appropriate OpenAI endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {app.config["OPENAI_API_KEY"]}'
    }
    data = {
        'prompt': context,
        'max_tokens': 50
    }
    response = requests.post(openai_url, json=data, headers=headers)
    return response.json()['choices'][0]['text'] if response.ok else None



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    descriptions='what do these words describe: '
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
