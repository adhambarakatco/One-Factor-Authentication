import psutil
import time
import requests
import json
import logging

# Configure logging to display timestamps and log levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Log system resource usage (CPU and RAM)
def log_system_resources():
    """Log the current CPU and RAM usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    logging.info(f"CPU Usage: {cpu_usage}%")
    logging.info(f"RAM Usage: {ram_usage}%")
    return cpu_usage, ram_usage

# Log the time taken to process a request
def log_request_time(start_time, end_time, url):
    """Log the duration of a request for a given URL."""
    processing_time = end_time - start_time
    logging.info(f"Request time for {url}: {processing_time:.4f} seconds")

# Enroll a user by sending their data to the server
def enroll(user_name, crypto_commitment):
    """
    Sends a user's name and cryptographic commitment to the server for enrollment.

    Args:
        user_name (str): The user's name.
        crypto_commitment (str): The cryptographic commitment.
    """
    server_url = 'http://localhost:5001/enroll'
    headers = {'Content-Type': 'application/json'}
    payload = {'user_name': user_name, 'crypto_commitment': crypto_commitment}

    start_time = time.time()
    log_system_resources()

    try:
        response = requests.post(server_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        end_time = time.time()
        log_request_time(start_time, end_time, server_url)
        log_system_resources()

        response_data = response.json()
        if 'message' in response_data:
            logging.info(f"Enrollment successful: {response_data['message']}")
        else:
            logging.error("No 'message' found in response during enrollment.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error enrolling: {e}")

# Verify user credentials during sign-in
def sign_in(user_name, user_secret):
    """
    Verify a user's credentials by generating a commitment and sending it to the server.

    Args:
        user_name (str): The user's name.
        user_secret (int): The user's secret value.
    """
    crypto_commitment = generate_crypto_commitment(user_secret)
    if not crypto_commitment:
        logging.error("Failed to generate crypto commitment for sign-in.")
        return

    start_time = time.time()
    log_system_resources()

    server_url = 'http://localhost:5001/verifyCommitment'
    headers = {'Content-Type': 'application/json'}
    payload = {'user_name': user_name, 'crypto_commitment': crypto_commitment}

    try:
        response = requests.post(server_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        end_time = time.time()
        log_request_time(start_time, end_time, server_url)
        log_system_resources()

        response_data = response.json()
        if 'message' in response_data:
            logging.info(f"Sign-in successful: {response_data['message']}")
        else:
            logging.error("No 'message' found in response during sign-in.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error signing in: {e}")

# Generate a cryptographic commitment based on the user's secret
def generate_crypto_commitment(user_secret):
    """
    Generate a cryptographic commitment by sending the user's secret to the server.

    Args:
        user_secret (int): The user's secret value.

    Returns:
        str: The generated cryptographic commitment or None if an error occurs.
    """
    url = 'http://localhost:8080/generateCommitment'
    params = {'user_secret': user_secret}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'crypto_commitment' in data:
            return data['crypto_commitment']
        else:
            logging.error("Crypto commitment not found in response.")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating crypto commitment: {e}")
        return None

# Main function to manage user interactions for sign-up and sign-in
def main():
    """Provide a menu-driven interface for user sign-up and sign-in."""
    print("Choose an option:")
    print("1. Sign Up")
    print("2. Sign In")

    choice = input("Enter 1 or 2: ")

    if choice == '1':
        user_name = input("Enter username: ")
        try:
            user_secret = int(input("Enter secret (e.g., 123): "))
        except ValueError:
            logging.error("Invalid secret format. Please enter a number.")
            return

        crypto_commitment = generate_crypto_commitment(user_secret)

        if crypto_commitment:
            logging.info(f"Generated crypto commitment: {crypto_commitment}")
            enroll(user_name, crypto_commitment)
        else:
            logging.error("Failed to generate crypto commitment during sign-up.")

    elif choice == '2':
        user_name = input("Enter username: ")
        try:
            user_secret = int(input("Enter secret: "))
        except ValueError:
            logging.error("Invalid secret format. Please enter a number.")
            return

        sign_in(user_name, user_secret)
    else:
        logging.error("Invalid choice. Please enter 1 or 2.")

if __name__ == '__main__':
    main()
