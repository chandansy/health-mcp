# **Personal Health MCP Server**
A personalized Model Context Protocol (MCP) server that connects Claude to my Garmin Forerunner 265 and tracks my Cult.fit body metrics.
By running this server in the cloud, you can use Claude's mobile app as a personalized AI fitness coach that has real-time access to your health data, recovery stats, and historical body composition.

## **🚀 Features**
- **Garmin Connect Integration:** Fetches daily stats (sleep, Body Battery, stress, resting HR) and recent activities (running pace, distance, VO2 Max).
- **Cult.fit Body Metrics Tracking:** Saves and tracks historical body composition data (weight, body fat %, muscle mass). Claude reads the Cult.fit PDFs natively on your phone and sends the extracted data to this server for long-term storage.
- **Cloud & Mobile Ready:** Designed to run on a cloud server (AWS/GCP) using Server-Sent Events (SSE), making it compatible with Claude's "Custom Connectors" for mobile access.
- **Secure:** Secured behind a custom API key authorization header.

## **📋 Prerequisites**
- Python 3.10 or higher
- A Garmin Connect account
- (For Mobile) A free cloud server (e.g., Google Cloud e2-micro) and a custom domain for HTTPS.

## **💻 Local Setup (For Claude Desktop)**
1. **Clone the repository:**  
   `git clone https://github.com/YOUR_USERNAME/health-mcp.git`  
   `cd health-mcp`
2. **Create a virtual environment and install dependencies:**  
   `python -m venv venv`  
   `source venv/bin/activate`  # On Windows use: `venv\Scripts\activate`  
   `pip install mcp garminconnect python-dotenv`
3. **Configure environment variables:**
   - Create a .env file in the root directory.
   - Add your Garmin credentials:  
     `GARMIN_EMAIL=your_email@example.com`  
     `GARMIN_PASSWORD=your_password`
4. **Add to Claude Desktop:**  
   Edit your `claude_desktop_config.json` to include this server, pointing to the absolute path of `health_mcp.py`.

## **☁️ Cloud Deployment (For Mobile App Access)**
To use this on the Claude mobile app, the server must be deployed to the cloud so your phone can reach it.
1. Clone this repository on your cloud server (e.g., GCP Free Tier).
2. Install the dependencies and create your .env file.
3. Run the server in SSE web mode:  
   `python health_mcp.py --serve`
4. Put the server behind a reverse proxy (like **Caddy**) to enable HTTPS (SSL) and enforce an Authorization Header (API Key) to keep your health data private.

## **📱 Connecting to Claude Mobile**
1. Go to [claude.ai](https://claude.ai) on your computer.
2. Click your profile -> **Settings** -> **Connectors**.
3. Click **Add custom connector**.
4. **URL:** Enter your server's secure URL (e.g., `https://health.yourdomain.com/sse`).
5. **Headers:** Add your secret API key.
   - Key: Authorization
   - Value: Bearer YOUR_SECRET_API_KEY
6. Open the Claude app on your phone, start a chat, and select your new Custom Connector!

## **⚠️ Security Warning**
**Never** commit your `.env` file or your `health_history.json` file to GitHub. Ensure they are listed in your `.gitignore` file before pushing your code.
