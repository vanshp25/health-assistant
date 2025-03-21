from boltiotai import openai
import os
from flask import Flask, render_template_string, request, jsonify

# Configure OpenAI API key using environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to create health assistant responses based on user input
def create_health_response(conversation_history):
    messages = [{"role": "system", "content": "You are a helpful health assistant."}]
    messages.extend(conversation_history)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Initialize Flask app and define route for the root URL handling GET and POST
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Personal Health Assistant</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script>
            async function sendUserMessage() {
                const userMessage = document.querySelector('#userMessage').value;
                if (!userMessage.trim()) return;

                const chatBox = document.querySelector('#chatBox');
                const userDiv = document.createElement('div');
                userDiv.className = 'alert alert-primary';
                userDiv.textContent = userMessage;
                chatBox.appendChild(userDiv);

                document.querySelector('#userMessage').value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({message: userMessage})
                });

                const data = await response.json();
                const assistantDiv = document.createElement('div');
                assistantDiv.className = 'alert alert-secondary';
                assistantDiv.textContent = data.response;
                chatBox.appendChild(assistantDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1 class="my-4">Personal Health Assistant</h1>
            <div id="chatBox" class="mb-3" style="max-height: 400px; overflow-y: scroll;"></div>
            <div class="input-group mb-3">
                <input type="text" class="form-control" id="userMessage" placeholder="Type your message here...">
                <button class="btn btn-primary" type="button" onclick="sendUserMessage()">Send</button>
            </div>
        </div>
    </body>
    </html>
    ''')

# Endpoint for processing chat messages
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if 'conversation' not in request.cookies:
        conversation_history = [{"role": "assistant", "content": "Hello! How can I assist you with your health today?"}]
    else:
        conversation_history = eval(request.cookies.get('conversation'))

    conversation_history.append({"role": "user", "content": user_message})
    assistant_response = create_health_response(conversation_history)
    conversation_history.append({"role": "assistant", "content": assistant_response})

    response = jsonify({'response': assistant_response})
    response.set_cookie('conversation', str(conversation_history))

    return response

# Run the Flask app if executed as the main program
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
