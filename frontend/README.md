# MultiLLM Router Frontend

A lightweight, modern web interface for interacting with the MultiLLM Router API.

## Features

- 💬 **Chat Interface** - Clean, intuitive chat interface for conversing with LLMs
- 🔄 **Streaming Support** - Real-time streaming responses for better UX
- 📊 **Model Information** - View which model was selected and why
- 🔌 **Flexible API Connection** - Connect to any MultiLLM API instance
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 🎨 **Modern UI** - Beautiful, clean interface with smooth animations

## Quick Start

### Option 1: Using Python HTTP Server (Recommended)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start a simple HTTP server:
```bash
# Python 3
python3 -m http.server 8080

# Or Python 2
python -m SimpleHTTPServer 8080
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

### Option 2: Using Node.js http-server

1. Install http-server globally (if not already installed):
```bash
npm install -g http-server
```

2. Navigate to the frontend directory:
```bash
cd frontend
```

3. Start the server:
```bash
http-server -p 8080
```

4. Open your browser and navigate to:
```
http://localhost:8080
```

### Option 3: Open Directly in Browser

Simply open `index.html` in your browser. Note: Some features may not work due to CORS restrictions if the API is on a different origin.

## Configuration

### Setting API URL

1. Enter your API URL in the header input field (default: `http://localhost:8000`)
2. Click "Connect" to verify the connection
3. The URL is automatically saved in your browser's localStorage

### Using the Interface

1. **Check System Status**: The sidebar shows API health and available models
2. **Load Models**: Click "Load Models" to see all available LLM models
3. **Send Messages**: Type your message and press Enter or click Send
4. **Streaming**: Toggle "Stream Response" for real-time streaming responses
5. **Clear Chat**: Click "Clear" to start a new conversation

## API Endpoints Used

The frontend interacts with the following API endpoints:

- `GET /api/v1/health` - Check API health and status
- `GET /api/v1/models` - Get list of available models
- `POST /api/v1/chat` - Send chat messages (non-streaming)
- `POST /api/v1/chat/stream` - Send chat messages (streaming)

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Styling and layout
├── app.js          # Application logic
└── README.md       # This file
```

## Features in Detail

### Chat Interface
- Clean message bubbles with distinct styling for user and assistant messages
- Metadata display showing model, provider, response time, and cost
- Smooth animations and transitions
- Auto-scroll to latest messages

### Streaming Responses
- Real-time token-by-token display
- Loading indicators during generation
- Metadata updates as model selection happens
- Graceful error handling

### Model Information Sidebar
- Current model details
- Routing reasoning
- Performance metrics
- System status and uptime

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure your MultiLLM API has CORS enabled. The API should already have CORS middleware configured to allow all origins.

### Connection Issues
1. Verify the API URL is correct
2. Ensure the MultiLLM API server is running
3. Check the browser console for detailed error messages
4. Verify the API is accessible from your browser

### Streaming Not Working
1. Ensure your browser supports Server-Sent Events (SSE) or Fetch API streaming
2. Check that the API endpoint `/api/v1/chat/stream` is working
3. Try disabling streaming and using regular chat mode

## Customization

You can customize the frontend by modifying:

- **Colors**: Edit CSS variables in `styles.css` (root `:root` selector)
- **API Endpoints**: Modify the API calls in `app.js`
- **UI Layout**: Adjust the HTML structure in `index.html`

## License

Part of the MultiLLM Router project.
