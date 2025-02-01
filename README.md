# One Factor Authentication using Zero-Knowledge Proofs (ZKP)

This project demonstrates the use of Zero-Knowledge Proofs (ZKPs) for secure one-factor authentication. The system enables users to authenticate without revealing sensitive personal data, leveraging cryptographic techniques to ensure privacy and security.

### Key Components:
- **Client Application (Python)**: The interface for the user to interact with the system. It handles user registration, secret commitment generation, and authentication requests.
- **Server Application (Python)**: Manages user requests, processes enrollment, and verifies user authentication by comparing cryptographic commitments.
- **ZKP Integration (Go)**: Uses the gnark library to generate and verify cryptographic commitments based on user secrets.
- **Database (SQLite)**: Stores cryptographic commitments securely, allowing for effective user authentication.

### Technologies Used:
- **Python**: Handles client-server communication, manages system resources (CPU and RAM), and logs request times.
- **SQLite**: A lightweight database used to store cryptographic commitments securely.
- **gnark (Go)**: A cryptographic library used to generate commitments via Zero-Knowledge Proofs.
- **HTTP Server (Python/Go)**: Facilitates communication between the client and server.

---

## Installation Instructions

### Prerequisites:
- Python 3.x
- Go 1.16+
- SQLite3 (for database handling)
- pip (Python package manager)

### Setup:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/adhambarakatco/One-Factor-Authentication.git
   ```

2. **Install required dependencies**:

   - For Python:
     ```bash
     pip install -r requirements.txt
     ```

   - For Go (Ensure you have Go installed):
     ```bash
     go get github.com/consensys/gnark
     ```

3. **Run the Server**:
   - To start the Python-based server, run:
     ```bash
     python server.py
     ```
   - To start the Go-based server, run:
     ```bash
     go run main.go
     ```

4. **Run the Client**:
   To interact with the system, run the Python client:
   ```bash
   python client.py
   ```

---

## Usage Instructions

The system provides the following functionalities:

1. **Sign-Up**:
   - Users can register by providing a username and secret number.
   - The client generates a cryptographic commitment of the secret and sends it to the server for secure storage.
   
2. **Sign-In**:
   - During authentication, the client generates a new commitment using the provided secret and compares it against the stored commitment on the server.
   - If the commitments match, authentication is successful.

---

## System Architecture

1. **Client**:
   - Accepts user input (username and secret).
   - Generates cryptographic commitments using the ZKP protocol.
   - Sends the commitment to the server for enrollment or authentication.
   
2. **Server**:
   - Stores the user's cryptographic commitment.
   - Verifies user credentials during login by comparing the commitment stored in the database.
   
3. **ZKP Integration (Go)**:
   - The Go server is responsible for generating cryptographic commitments using the gnark library.
   - The commitment is generated as the square of the user's secret and is verified during the sign-in process.

---

## Metrics and Performance

### Performance Metrics:
- **CPU and RAM Usage**: Monitored and logged for both the client and server.
- **Request Handling Time**: Time taken to process each user request (for enrollment and authentication) is logged.
- **Packet Propagation**: The system evaluates packet propagation times for communication between the client and server.

### Efficiency:
- The current system handles requests in an average of 2 seconds but has potential for optimizations in terms of algorithmic efficiency and system resource management.

---

## Future Directions
- **Scalability Improvements**: Optimizing the system to handle high user loads efficiently.
- **Enhanced Security**: Integrating advanced security protocols to improve overall privacy protection.
- **Mobile Support**: Developing a mobile-friendly version of the client for better accessibility.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
