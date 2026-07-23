import os
import json
import logging
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from garminconnect import Garmin
from dotenv import load_dotenv

# Load environment variables (Garmin credentials)
load_dotenv()

# Initialize the MCP Server
mcp = FastMCP("PersonalHealthServer")

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File to store historical body metrics on your cloud server
HISTORY_FILE = "health_history.json"

def get_garmin_client() -> Garmin:
    """Helper function to authenticate with Garmin Connect."""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    
    if not email or not password:
        raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set in environment variables.")
    
    client = Garmin(email, password)
    client.login()
    return client

@mcp.tool()
def get_garmin_daily_summary(date_iso: str) -> str:
    """
    Get daily health summary from Garmin (Steps, HR, Body Battery, Sleep, Stress).
    
    Args:
        date_iso: Date in YYYY-MM-DD format (e.g., '2026-07-23').
    """
    try:
        client = get_garmin_client()
        stats = client.get_stats(date_iso)
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error fetching Garmin daily summary: {str(e)}"

@mcp.tool()
def get_garmin_recent_activities(limit: int = 5) -> str:
    """
    Get recent logged workouts and activities from the Forerunner 265.
    Useful for analyzing recent running performance, pace, and load.
    
    Args:
        limit: Number of recent activities to fetch (default is 5).
    """
    try:
        client = get_garmin_client()
        activities = client.get_activities(0, limit)
        return json.dumps(activities, indent=2)
    except Exception as e:
        return f"Error fetching Garmin activities: {str(e)}"

# NOTE: Claude will read the Cult.fit PDF natively on your phone 
# and pass the extracted data directly to the tool below.

@mcp.tool()
def save_body_metrics_snapshot(date_iso: str, metrics: dict) -> str:
    """
    Saves a snapshot of body metrics (weight, fat %, muscle mass, etc.) 
    to a database on the cloud server. 
    
    Claude MUST call this tool AFTER the user uploads a Cult.fit PDF 
    and Claude has natively extracted the parameters from the document.
    
    Args:
        date_iso: The date of the reading (YYYY-MM-DD).
        metrics: A dictionary containing the parameters extracted from the PDF.
    """
    try:
        history = {}
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
                
        history[date_iso] = metrics
        
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
            
        return f"Successfully saved body metrics for {date_iso} to the cloud database. Total records: {len(history)}"
    except Exception as e:
        return f"Error saving metrics snapshot: {str(e)}"

@mcp.tool()
def get_body_metrics_history() -> str:
    """
    Retrieves the historical body metrics saved over time.
    Use this to analyze trends in body fat, muscle mass, and weight over time.
    """
    if not os.path.exists(HISTORY_FILE):
        return "No historical health data found. Please upload a PDF and save a snapshot first."
        
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return json.dumps(history, indent=2)
    except Exception as e:
        return f"Error reading health history: {str(e)}"

if __name__ == "__main__":
    import sys
    
    # Run with 'python health_mcp.py --serve' for Cloud deployment
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        logger.info("Starting MCP Server in SSE mode on port 8000...")
        mcp.run(transport='sse', host="0.0.0.0", port=8000)
    else:
        # Default: Run via standard input/output for local Claude Desktop
        mcp.run()
