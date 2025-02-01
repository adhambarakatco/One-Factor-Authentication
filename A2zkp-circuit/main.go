package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"

	"github.com/consensys/gnark-crypto/ecc"
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/frontend/cs/r1cs"
)

// Circuit defines the structure of the cryptographic circuit used for commitment generation
type Circuit struct {
	UserSecret       frontend.Variable `gnark:"user_secret,private"`      // UserSecret is a private input to the circuit
	CryptoCommitment frontend.Variable `gnark:"crypto_commitment,public"` // CryptoCommitment is the public output of the circuit
}

// Define specifies the constraint logic of the circuit
func (c *Circuit) Define(api frontend.API) error {
	// Constraint: CryptoCommitment = UserSecret^2
	api.AssertIsEqual(c.CryptoCommitment, api.Mul(c.UserSecret, c.UserSecret))
	return nil
}

// GenerateCryptoCommitment generates a cryptographic commitment based on the provided user secret
func GenerateCryptoCommitment(userSecret int64) (string, error) {
	var circuit Circuit
	// Compile the circuit using the BN254 scalar field
	_, compileErr := frontend.Compile(ecc.BN254.ScalarField(), r1cs.NewBuilder, &circuit)
	if compileErr != nil {
		return "", compileErr
	}

	// Assign the input values to the circuit
	assignment := Circuit{
		UserSecret:       userSecret,
		CryptoCommitment: userSecret * userSecret, // Example: commitment = user_secret^2
	}

	// Create a witness to represent the inputs to the circuit
	witness, witnessErr := frontend.NewWitness(&assignment, ecc.BN254.ScalarField())
	if witnessErr != nil {
		return "", witnessErr
	}

	// Extract the public output (commitment) from the witness
	publicWitness, _ := witness.Public()
	return fmt.Sprintf("%v", publicWitness), nil
}

// verifyCryptoCommitment validates whether the provided commitment matches the stored commitment
func verifyCryptoCommitment(correctCryptoCommitment string, storedCryptoCommitment string) bool {
	// Compare the provided commitment with the stored commitment
	return correctCryptoCommitment == storedCryptoCommitment
}

// generateCommitmentHandler handles HTTP requests for generating a cryptographic commitment
func generateCommitmentHandler(w http.ResponseWriter, r *http.Request) {
	// Extract the "user_secret" query parameter from the request
	secretStr := r.URL.Query().Get("user_secret")
	userSecret, parseErr := strconv.ParseInt(secretStr, 10, 64)
	if parseErr != nil {
		http.Error(w, "Invalid secret value", http.StatusBadRequest)
		return
	}

	// Generate the cryptographic commitment
	cryptoCommitment, genErr := GenerateCryptoCommitment(userSecret)
	if genErr != nil {
		http.Error(w, fmt.Sprintf("Error generating crypto commitment: %v", genErr), http.StatusInternalServerError)
		return
	}

	// Return the generated commitment as a JSON response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"crypto_commitment": cryptoCommitment})
}

// VerifyRequest represents the structure of a JSON request for verifying commitments
type VerifyRequest struct {
	CryptoCommitment       string `json:"crypto_commitment"`        // The commitment provided for verification
	StoredCryptoCommitment string `json:"stored_crypto_commitment"` // The stored commitment for comparison
}

// verifyCommitmentHandler handles HTTP requests for verifying cryptographic commitments
func verifyCommitmentHandler(w http.ResponseWriter, r *http.Request) {
	// Decode the JSON request body into a VerifyRequest struct
	var req VerifyRequest
	decoder := json.NewDecoder(r.Body)
	decodeErr := decoder.Decode(&req)
	if decodeErr != nil {
		http.Error(w, "Invalid JSON data", http.StatusBadRequest)
		return
	}

	// Verify the provided commitment against the stored commitment
	isValid := verifyCryptoCommitment(req.CryptoCommitment, req.StoredCryptoCommitment)
	if isValid {
		// Respond with a success status if the commitment is valid
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{"status": "Commitment is valid"})
	} else {
		// Respond with an error if the commitment is invalid
		http.Error(w, "Invalid commitment", http.StatusUnauthorized)
	}
}

func main() {
	// Register HTTP handlers for the endpoints
	http.HandleFunc("/generateCommitment", generateCommitmentHandler)
	http.HandleFunc("/verifyCommitment", verifyCommitmentHandler)

	// Start the HTTP server on port 8080
	port := ":8080"
	log.Println("Server is starting on port", port)
	serverErr := http.ListenAndServe(port, nil)
	if serverErr != nil {
		log.Fatal("Error starting server:", serverErr)
	}
}
