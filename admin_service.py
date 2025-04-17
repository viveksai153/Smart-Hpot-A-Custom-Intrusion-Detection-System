import sqlite3
from flask import Flask, jsonify, render_template
from flask_cors import CORS  # Import CORS module

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Database file
DB_FILE = "honeypot_logs.db"

# ======================[ Database Fetching Function ]======================

def fetch_logs(table_name):
    """Fetch all logs from a given table."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [desc[0] for desc in cursor.description]  # Fetch column names
            logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return logs
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}

# ======================[ API Endpoints ]======================

@app.route('/')
def home():
    """Render the admin dashboard."""
    return render_template("dashboard.html")

@app.route('/logs/ssh', methods=['GET'])
def get_ssh_logs():
    """Fetch all SSH logs."""
    return jsonify(fetch_logs("ssh_logs"))

@app.route('/logs/http', methods=['GET'])
def get_http_logs():
    """Fetch all HTTP logs."""
    return jsonify(fetch_logs("http_logs"))

@app.route('/logs/network', methods=['GET'])
def get_network_logs():
    """Fetch all Network logs."""
    return jsonify(fetch_logs("network_logs"))

@app.route('/clear_logs/<log_type>', methods=['DELETE'])
def clear_logs(log_type):
    """Clear logs for a specific type: ssh, http, or network."""
    if log_type not in ["ssh", "http", "network"]:
        return jsonify({"error": "Invalid log type"}), 400

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {log_type}_logs")  # Clear logs
            conn.commit()
        return jsonify({"message": f"{log_type.upper()} logs cleared successfully!"})
    except sqlite3.Error as e:
        return jsonify({"error": f"Failed to clear logs: {str(e)}"}), 500

# ======================[ Run the Flask Server ]======================

if __name__ == "__main__":
    print("📊 [ADMIN PANEL] Running on http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
