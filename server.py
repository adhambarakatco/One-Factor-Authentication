import sqlite3
import json
import psutil
import time
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configure logging with timestamps and message levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the SQLite database and create the table if it doesn't exist
def init_db():
    """Initialize the database and ensure the user_commitments table exists."""
    db_conn = sqlite3.connect('commitments.db')
    db_cursor = db_conn.cursor()
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_commitments (
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            crypto_commitment TEXT NOT NULL
        )
    ''')
    db_conn.commit()
    db_conn.close()

# Save a user's cryptographic commitment to the database
def save_crypto_commitment(user_name, crypto_commitment):
    """Insert a user's name and their cryptographic commitment into the database."""
    db_conn = sqlite3.connect('commitments.db')
    db_cursor = db_conn.cursor()
    db_cursor.execute('INSERT INTO user_commitments (user_name, crypto_commitment) VALUES (?, ?)', (user_name, crypto_commitment))
    db_conn.commit()
    db_conn.close()

# Retrieve the stored commitment for a user from the database
def verify_crypto_commitment(user_name):
    """
    Fetch the cryptographic commitment associated with the given username.
    
    Returns:
        str: The stored commitment if found, otherwise None.
    """
    db_conn = sqlite3.connect('commitments.db')
    db_cursor = db_conn.cursor()
    db_cursor.execute('SELECT crypto_commitment FROM user_commitments WHERE user_name = ?', (user_name,))
    stored_crypto_commitment = db_cursor.fetchone()
    db_conn.close()

    if stored_crypto_commitment:
        return stored_crypto_commitment[0]
    return None

# Check if a user already exists in the database
def user_exists(user_name):
    """Verify if a username exists in the database."""
    db_conn = sqlite3.connect('commitments.db')
    db_cursor = db_conn.cursor()
    db_cursor.execute('SELECT 1 FROM user_commitments WHERE user_name = ?', (user_name,))
    exists = db_cursor.fetchone() is not None
    db_conn.close()
    return exists

# Log the server's CPU and RAM usage
def log_system_resources():
    """Log the current CPU and RAM usage of the server."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    logging.info(f"Server CPU Usage: {cpu_usage}%")
    logging.info(f"Server RAM Usage: {ram_usage}%")
    return cpu_usage, ram_usage

# Log the time taken to process a request
def log_request_time(start_time, end_time, url):
    """Log the duration of a request for a specific endpoint."""
    processing_time = end_time - start_time
    logging.info(f"Request time for {url}: {processing_time:.4f} seconds")

# Custom HTTP request handler for enrollment and verification
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for enrollment and verification."""
        start_time = time.time()

        if self.path == '/enroll':
            # Handle user enrollment
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            user_name = data.get('user_name')
            crypto_commitment = data.get('crypto_commitment')

            if not user_name or not crypto_commitment:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing username or crypto commitment"}).encode())
                return

            if user_exists(user_name):
                self.send_response(409)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "User already exists"}).encode())
                return

            save_crypto_commitment(user_name, crypto_commitment)

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Crypto commitment and username saved successfully!"}).encode())

        elif self.path == '/verifyCommitment':
            # Handle commitment verification
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            user_name = data.get('user_name')
            crypto_commitment = data.get('crypto_commitment')

            if not user_name:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing username"}).encode())
                return

            stored_crypto_commitment = verify_crypto_commitment(user_name)

            if stored_crypto_commitment == crypto_commitment:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Login Successful"}).encode())
            else:
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())

        # Log the processing time and system resources after handling the request
        end_time = time.time()
        log_request_time(start_time, end_time, self.path)
        log_system_resources()

    def do_GET(self):
        """Handle GET requests for server status."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Server is running")

# Start the server and handle requests
def run(server_class=HTTPServer, handler_class=RequestHandler, port=5001):
    """Initialize the database and start the HTTP server."""
    init_db()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
