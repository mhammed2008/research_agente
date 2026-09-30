# TeknoNFC — Function Encyclopedia: Cryptographic Vault

> **Module**: `internal/crypto`  
> **Source Files**: [`internal/crypto/nfc_crypto.go`](file:///d:/teknoKeys/GO-NFC/internal/crypto/nfc_crypto.go), [`internal/crypto/crypto_test.go`](file:///d:/teknoKeys/GO-NFC/internal/crypto/crypto_test.go)  
> **Classification**: Zero-Omission Cryptographic Symbol Catalog  
> **Standards Compliance**: NIST SP 800-38B (AES-CMAC) • RFC 4493 • EMV Contactless KDF

---

## Symbol Manifest

| Symbol Name | Kind | Line Range | Visibility | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Zeroize` | Function | L22 - L26 | Public | Secure memory overwrite of byte slices |
| `GenerateNonce` | Function | L29 - L34 | Public | Generates 64-bit CSPRNG hex challenge nonces |
| `NormalizeAmount` | Function | L37 - L54 | Public | Fixed-point 4-decimal currency string normalizer |
| `ComputeCryptogram` | Function | L57 - L62 | Public | Generates HMAC-SHA256 tap authentication cryptogram |
| `VerifyCryptogram` | Function | L65 - L71 | Public | Constant-time HMAC-SHA256 cryptogram verification |
| `DeriveSessionKey` | Function | L75 - L92 | Public | AES-128 KDF session key derivation per ATC |
| `AmountToMinorUnits` | Function | L95 - L106 | Public | Converts decimal currency strings to integer minor units |
| `BuildChallengeVector` | Function | L109 - L127 | Public | Formats binary EMV challenge vector for ARQC |
| `ComputeHceArqc` | Function | L130 - L145 | Public | Computes 8-byte AES-128 CMAC HCE ARQC cryptogram |
| `VerifyHceArqc` | Function | L148 - L162 | Public | Constant-time HCE ARQC validation primitive |
| `GenerateTokenizedDPAN` | Function | L165 - L172 | Public | Generates 16-digit tokenized surrogate card number |
| `MaskDPAN` | Function | L175 - L180 | Public | Masks 16-digit DPAN showing first 6 and last 4 digits |
| `AES128CMAC` | Function | L183 - L239 | Public | NIST SP 800-38B / RFC 4493 AES-128 CMAC engine |
| `generateSubkey` | Function | L241 - L262 | Private | Derives subkeys K1 and K2 with Galois field multiplication |
| `TruncateOddBytes` | Function | L265 - L273 | Public | Extracts bytes at odd indices [1,3,5,7,9,11,13,15] (NXP SUN) |
| `MaskUID` | Function | L276 - L281 | Public | Masks silicon NFC UID preserving first 4 and last 4 chars |
| `MaskPhone` | Function | L284 - L290 | Public | Masks phone numbers for PCI DSS log safety |
| `GenerateRandomAES128Key` | Function | L293 - L298 | Public | Generates 16-byte cryptographically secure random AES key |
| `GenerateCardUID` | Function | L301 - L306 | Public | Generates random 7-byte contactless card UID |
| `UUIDv4` | Function | L309 - L321 | Public | Generates RFC 4122 compliant UUID version 4 |
| `SimpleChallenge` | Function | L324 - L328 | Public | Generates 8-byte hex challenge nonce |
| `VerifyConstantTime` | Function | L370 - L376 | Public | Constant-time string comparison resisting timing attacks |
| `GenerateNumericCode` | Function | L380 - L397 | Public | Generates unguessable n-digit CSPRNG verification code |
| `TestRFC4493Vectors` | Test | L12 - L48 | Public | Validates AES-CMAC against NIST test vectors |
| `TestOddByteTruncation` | Test | L50 - L65 | Public | Tests odd-byte truncation indices [1,3,5,7,9,11,13,15] |
| `TestCryptogramVerification` | Test | L67 - L82 | Public | Validates cryptogram matching and rejection logic |
| `TestDeriveSessionKeyAndHceArqc` | Test | L84 - L115 | Public | Tests full session KDF and ARQC end-to-end verification |

---

## Detailed Symbol Specifications

### `Zeroize`
```go
func Zeroize(b []byte)
```
- **Location**: `internal/crypto/nfc_crypto.go#L22-L26`
- **Purpose**: Explicitly wipes sensitive key buffers in memory with zeros (`0x00`) to prevent memory dumps from extracting cryptographic material.
- **Parameters**: `b []byte` — target slice to zeroize.
- **Side Effects**: Overwrites memory directly in-place.

### `GenerateNonce`
```go
func GenerateNonce() (string, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L29-L34`
- **Purpose**: Generates an 8-byte (64-bit) high-entropy cryptographic nonce using `crypto/rand`.
- **Return Value**: `(string, error)` — 16-character uppercase hex nonce.

### `NormalizeAmount`
```go
func NormalizeAmount(val interface{}) string
```
- **Location**: `internal/crypto/nfc_crypto.go#L37-L54`
- **Purpose**: Converts arbitrary numeric inputs (float, int, string) into fixed-point 4-decimal currency strings (e.g. `"25.0000"`), eliminating floating-point IEEE-754 precision errors.
- **Return Value**: `string` — Normalized currency string.

### `ComputeCryptogram`
```go
func ComputeCryptogram(nonce string, receiverID int64, amount string, atc uint64, keyHex string) string
```
- **Location**: `internal/crypto/nfc_crypto.go#L57-L62`
- **Purpose**: Generates an HMAC-SHA256 signature binding the nonce, receiver ID, amount, and ATC sequence.
- **Return Value**: `string` — Hex-encoded MAC.

### `VerifyCryptogram`
```go
func VerifyCryptogram(receivedCryptogram, nonce string, receiverID int64, amount string, atc uint64, keyHex string) bool
```
- **Location**: `internal/crypto/nfc_crypto.go#L65-L71`
- **Purpose**: Validates received cryptograms in constant time using `subtle.ConstantTimeCompare`.
- **Return Value**: `bool` — `true` if valid, `false` otherwise.

### `DeriveSessionKey`
```go
func DeriveSessionKey(masterKeyHex string, atc uint64) ([]byte, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L75-L92`
- **Purpose**: Implements EMV contactless Key Derivation Function (`KDF`). Encrypts a 16-byte derivation block containing the ATC using the card's 128-bit Master Derivation Key (`MDK`).
- **Return Value**: `([]byte, error)` — 16-byte session key.

### `AmountToMinorUnits`
```go
func AmountToMinorUnits(amountStr string) uint32
```
- **Location**: `internal/crypto/nfc_crypto.go#L95-L106`
- **Purpose**: Converts decimal amounts (e.g. `"25.50"`) into integer minor currency units (cents, e.g. `2550`).
- **Return Value**: `uint32` — Amount in minor units.

### `BuildChallengeVector`
```go
func BuildChallengeVector(amount uint32, currencyCode uint16, recipientTag string, nonceHex string) ([]byte, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L109-L127`
- **Purpose**: Constructs the 32-byte EMV contactless challenge block: 4 bytes amount, 2 bytes currency code, 8 bytes recipient tag, 8 bytes binary challenge nonce, 10 bytes zero padding.
- **Return Value**: `([]byte, error)` — 32-byte challenge vector.

### `ComputeHceArqc`
```go
func ComputeHceArqc(sessionKey, challengeVector []byte, atc uint64, dpan string) ([]byte, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L130-L145`
- **Purpose**: Computes an 8-byte Application Request Cryptogram (`ARQC`) by calculating the AES-128 CMAC over the challenge vector, ATC, and DPAN, truncating the result to 8 bytes.
- **Return Value**: `([]byte, error)` — 8-byte ARQC.

### `VerifyHceArqc`
```go
func VerifyHceArqc(receivedHex string, sessionKey, challengeVector []byte, atc uint64, dpan string) bool
```
- **Location**: `internal/crypto/nfc_crypto.go#L148-L162`
- **Purpose**: Computes expected ARQC and performs constant-time comparison against received cryptogram.
- **Return Value**: `bool` — `true` if valid.

### `GenerateTokenizedDPAN`
```go
func GenerateTokenizedDPAN() string
```
- **Location**: `internal/crypto/nfc_crypto.go#L165-L172`
- **Purpose**: Generates a 16-digit tokenized surrogate card number starting with BIN prefix `492188`.
- **Return Value**: `string` — 16-digit DPAN.

### `MaskDPAN`
```go
func MaskDPAN(dpan string) string
```
- **Location**: `internal/crypto/nfc_crypto.go#L175-L180`
- **Purpose**: Formats DPAN per PCI DSS v4.0.1 Requirement 3.4 (`492188******8810`).
- **Return Value**: `string` — Masked PAN string.

### `AES128CMAC`
```go
func AES128CMAC(key, message []byte) ([]byte, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L183-L239`
- **Purpose**: Pure Go implementation of RFC 4493 / NIST SP 800-38B Cipher-based Message Authentication Code (`CMAC`) algorithm.
- **Return Value**: `([]byte, error)` — 16-byte MAC tag.

### `generateSubkey`
```go
func generateSubkey(key []byte) ([]byte, []byte, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L241-L262`
- **Purpose**: Derives CMAC subkeys $K_1$ and $K_2$ using left-shift and constant XOR with $R_{128} = 0x87$.

### `TruncateOddBytes`
```go
func TruncateOddBytes(cmac []byte) []byte
```
- **Location**: `internal/crypto/nfc_crypto.go#L265-L273`
- **Purpose**: Extracts bytes at odd indices `[1, 3, 5, 7, 9, 11, 13, 15]` per NXP NTAG 424 DNA AN12196 standard.
- **Return Value**: `[]byte` — 8-byte SDMMAC.

### `MaskUID`
```go
func MaskUID(uid string) string
```
- **Location**: `internal/crypto/nfc_crypto.go#L276-L281`
- **Purpose**: Masks contactless card UID (e.g. `04A1******E5F6`).

### `MaskPhone`
```go
func MaskPhone(phone string) string
```
- **Location**: `internal/crypto/nfc_crypto.go#L284-L290`
- **Purpose**: Masks phone numbers for audit logging safety (`+1-555-****`).

### `GenerateRandomAES128Key`
```go
func GenerateRandomAES128Key() (string, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L293-L298`
- **Purpose**: Generates 16 random bytes via CSPRNG and formats as a 32-character hex string.

### `GenerateCardUID`
```go
func GenerateCardUID() string
```
- **Location**: `internal/crypto/nfc_crypto.go#L301-L306`
- **Purpose**: Generates a 7-byte hex string representing an ISO 14443 Type A contactless UID.

### `UUIDv4`
```go
func UUIDv4() string
```
- **Location**: `internal/crypto/nfc_crypto.go#L309-L321`
- **Purpose**: Generates an RFC 4122 compliant UUID version 4 with cryptographically secure bits.

### `SimpleChallenge`
```go
func SimpleChallenge() string
```
- **Location**: `internal/crypto/nfc_crypto.go#L324-L328`
- **Purpose**: Generates an 8-byte hex challenge nonce.

### `VerifyConstantTime`
```go
func VerifyConstantTime(a, b string) bool
```
- **Location**: `internal/crypto/nfc_crypto.go#L370-L376`
- **Purpose**: Compares two strings in constant time using `subtle.ConstantTimeCompare`, resisting timing attacks.

### `GenerateNumericCode`
```go
func GenerateNumericCode(digits int) (string, error)
```
- **Location**: `internal/crypto/nfc_crypto.go#L380-L397`
- **Purpose**: Generates an unguessable decimal numeric string (e.g. 6-digit confirmation code) using `crypto/rand`.

### `TestRFC4493Vectors`
```go
func TestRFC4493Vectors(t *testing.T)
```
- **Location**: `internal/crypto/crypto_test.go#L12-L48`
- **Purpose**: Validates AES-128 CMAC implementation against official RFC 4493 test vectors.

### `TestOddByteTruncation`
```go
func TestOddByteTruncation(t *testing.T)
```
- **Location**: `internal/crypto/crypto_test.go#L50-L65`
- **Purpose**: Validates NXP NTAG 424 odd-byte truncation.

### `TestCryptogramVerification`
```go
func TestCryptogramVerification(t *testing.T)
```
- **Location**: `internal/crypto/crypto_test.go#L67-L82`
- **Purpose**: Tests HMAC cryptogram generation, verification, and rejection.

### `TestDeriveSessionKeyAndHceArqc`
```go
func TestDeriveSessionKeyAndHceArqc(t *testing.T)
```
- **Location**: `internal/crypto/crypto_test.go#L84-L115`
- **Purpose**: End-to-end integration test validating session key derivation and HCE ARQC computation.
