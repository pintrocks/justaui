from flask import Flask, render_template_string, request, jsonify
from langchain_community.llms.ollama import Ollama

app = Flask(__name__)

# Initialize a model instance
default_model = "phi3:latest"  # Set a default model

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with Ollama</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap" rel="stylesheet">
    <style>
        body {
            display: flex;
            height: 100vh;
            flex-direction: column;
            background-color: #2b2b2b; /* Set background color to match chat box */
            font-family: 'Montserrat', sans-serif; /* Use Montserrat font */
        }
        .chat-box {
            height: calc(100vh - 150px); /* Adjust for the input area */
            overflow-y: auto;
            background: #2b2b2b; /* Dark background for chat */
            border-radius: 8px;
            padding: 10px;
            display: block; /* Initially visible */
            flex-grow: 1; /* Allow chat box to expand */
            margin-top: 10px; /* Add margin for spacing */
        }
        .chat-bubble {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            padding: 10px; /* Add padding for spacing */
            position: relative; /* Enable absolute positioning of the circle */
            opacity: 0; /* Start hidden for animation */
            animation: fadeIn 0.3s forwards; /* Fade in effect */
        }
        .user-bubble {
            justify-content: flex-end;
        }
        .ai-bubble {
            justify-content: flex-start;
        }
        .bubble-content {
            border-radius: 20px;
            max-width: 80%;
            word-wrap: break-word;
            position: relative;
            font-weight: bold; /* Make text bold */
            color: white; /* Set text color to white */
            padding: 10px; /* Add padding for bubble content */
            margin-left: 10px; /* Add space for the AI bubble */
            margin-right: 10px; /* Add space for the user bubble */
        }
        .user-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #007BFF; /* User color */
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            position: absolute; /* Position it absolutely */
            top: -20px; /* Adjust position above the bubble */
            right: 10px; /* Align it to the right */
            animation: bounce 0.6s infinite alternate; /* Bounce animation */
        }
        .ai-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #4CAF50; /* AI color */
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            margin-right: 10px;
            margin-bottom: 5px;
            animation: bounce 0.6s infinite alternate; /* Bounce animation */
        }
        .copy-button, .regenerate-button {
            margin-top: 5px;
            background-color: transparent; /* No background */
            color: white;
            border: none;
            padding: 5px; /* Adjust padding */
            cursor: pointer;
            display: inline-flex; /* Inline flex for icons */
            align-items: center; /* Center align items */
        }
        .copy-button:before {
            content: '\\f0c5'; /* Clipboard icon */
            font-family: "Font Awesome 5 Free"; /* Use Font Awesome for icons */
            font-weight: 900; /* Solid style */
        }
        .regenerate-button:before {
            content: '\\f021'; /* Regenerate icon */
            font-family: "Font Awesome 5 Free"; /* Use Font Awesome for icons */
            font-weight: 900; /* Solid style */
        }
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1F1F1F; /* Dark background for input area */
            padding: 10px;
        }
        .user-input {
            background-color: #333332; /* Background color for input */
            color: white; /* Text color */
            border-radius: 20px; /* Rounded corners */
            border: none; /* No border */
            padding: 10px; /* Padding for input */
            width: calc(100% - 60px); /* Width adjusted for button */
            font-size: 14px; /* Smaller font size */
        }
        .send-btn {
            background-color: white; /* White background */
            color: black; /* Black text */
            border: none; /* No border */
            border-radius: 50%; /* Make it round */
            width: 40px; /* Fixed width */
            height: 40px; /* Fixed height */
            display: flex; /* Flex for centering */
            align-items: center; /* Center vertically */
            justify-content: center; /* Center horizontally */
            cursor: pointer; /* Pointer cursor */
        }
        .loading {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 3px solid transparent;
            border-top: 3px solid #ffffff; /* White top border */
            animation: spin 0.8s linear infinite; /* Spin animation */
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer; /* Make it clickable */
        }
        .loader-lines {
            margin: 10px 0;
            height: 2px;
            background-color: brown; /* Color for loading lines */
            border-radius: 5px;
            animation: pulse 1.5s infinite;
        }
        /* Code block styles */
        .code-block {
            background-color: #282c34; /* Dark background for code block */
            color: #61dafb; /* Light blue text color */
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto; /* Allow horizontal scrolling */
            white-space: pre-wrap; /* Preserve whitespace */
            margin: 10px 0; /* Margin for spacing */
            font-family: 'Courier New', Courier, monospace; /* Monospace font for code */
        }
        @keyframes fadeIn {
            to {
                opacity: 1; /* Fade in effect */
            }
        }
        @keyframes bounce {
            0% {
                transform: translateY(0); /* Start at normal position */
            }
            100% {
                transform: translateY(-10px); /* Bounce up */
            }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="flex">
        <div class="flex-1 p-8">
            <div class="flex items-center justify-between">
                <div class="text-2xl font-bold mb-4 text-white">Model Name</div>
                <input type="text" id="model-input" class="bg-gray-800 text-white p-2 rounded" placeholder="Model Name" />
            </div>
            <div class="chat-box" id="chat-box"></div>
            <div class="input-area flex items-center">
                <input type="text" id="user-input" class="user-input" placeholder="Type your message here..." onkeypress="if(event.key === 'Enter'){sendMessage();}">
                <button id="send-btn" class="send-btn"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        let generating = false; // Flag to indicate if generating is in progress
        let currentModel = '{{ default_model }}'; // Set default model from Flask

        // Function to simulate the typewriter effect
        function typeWriter(text, element, speed) {
            let i = 0;
            element.innerHTML = ''; // Clear the element before starting
            function typing() {
                if (i < text.length) {
                    element.innerHTML += text.charAt(i);
                    i++;
                    setTimeout(typing, speed); // Call typing recursively with the specified speed
                }
            }
            typing();
        }

        // Function to create code block element
        function createCodeBlock(content) {
            const codeBlock = document.createElement('div');
            codeBlock.className = 'code-block';
            codeBlock.textContent = content; // Use textContent to avoid HTML parsing
            return codeBlock;
        }

        // Function to format the message
        function formatMessage(message) {
            const regex = /```([\s\S]*?)```/g; // Match code blocks with triple backticks
            const parts = message.split(regex); // Split the message into parts
            const formattedMessage = parts.map((part, index) => {
                if (index % 2 === 1) { // Odd index means it's a code block
                    return createCodeBlock(part); // Create a code block
                } else {
                    const span = document.createElement('span');
                    span.textContent = part; // Use textContent to avoid HTML parsing
                    return span; // Regular message
                }
            });

            return formattedMessage;
        }

        // Function to send the message
        async function sendMessage() {
            const userInput = document.getElementById('user-input');
            const message = userInput.value;

            if (message.trim() === '') return; // Prevent empty messages

            // Display user message
            const userBubble = document.createElement('div');
            userBubble.className = 'chat-bubble user-bubble';
            const userCircle = document.createElement('div');
            userCircle.className = 'user-circle'; 
            userCircle.textContent = 'U'; // User identifier
            const userContent = document.createElement('div');
            userContent.className = 'bubble-content';
            userContent.appendChild(...formatMessage(message));
            userBubble.appendChild(userCircle); // Add user circle
            userBubble.appendChild(userContent);
            chatBox.appendChild(userBubble);
            userInput.value = ''; // Clear input

            // Add loading indicator
            const loadingBubble = document.createElement('div');
            loadingBubble.className = 'chat-bubble ai-bubble';
            const loadingCircle = document.createElement('div');
            loadingCircle.className = 'ai-circle'; 
            loadingCircle.textContent = 'A'; // AI identifier
            const loadingContent = document.createElement('div');
            loadingContent.className = 'bubble-content';
            loadingContent.innerHTML = '<div class="loading"></div>'; // Add loading spinner
            loadingBubble.appendChild(loadingCircle); // Add AI circle
            loadingBubble.appendChild(loadingContent);
            chatBox.appendChild(loadingBubble);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom

            generating = true; // Set generating flag
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ model: currentModel, question: message })
            });
            const data = await response.json();

            // Remove loading bubble
            loadingBubble.remove();

            // Display AI response
            const aiBubble = document.createElement('div');
            aiBubble.className = 'chat-bubble ai-bubble';
            const aiCircle = document.createElement('div');
            aiCircle.className = 'ai-circle'; 
            aiCircle.textContent = 'A'; // AI identifier
            const aiContent = document.createElement('div');
            aiContent.className = 'bubble-content';
            typeWriter(data.answer, aiContent, 1); // Use typewriter effect for AI response
            aiBubble.appendChild(aiCircle); // Add AI circle
            aiBubble.appendChild(aiContent);
            chatBox.appendChild(aiBubble);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom

            generating = false; // Reset generating flag
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, default_model=default_model)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    model = data.get('model', default_model)
    question = data.get('question', '')
    
    # Use the model to generate a response (mock response for demonstration)
    llm = Ollama(model=model)
    answer = llm(question)  # This will use the chosen model
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
