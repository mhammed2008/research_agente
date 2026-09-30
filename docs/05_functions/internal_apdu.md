# Package internal/apdu Function & Symbol Reference

This document provides an exhaustive, zero-omission symbol reference for the `internal/apdu` package within TeknoNFC. The package handles ISO/IEC 7816-4 APDU (Application Protocol Data Unit — the packet format used to exchange commands and responses between NFC readers and smartcards) parsing, BER-TLV (Tag-Length-Value — the data encoding format used in smartcards) encoding/decoding, BCD (Binary Coded Decimal) currency conversions, and ISO 7816-4 status words.

---

## 1. Constants & Status Words

| Constant | Value | Description |
|---|---|---|
| `SWSuccess` | `"9000"` | Command successfully executed |
| `SWFileNotFound` | `"6A82"` | Application Identifier (AID) or file not found |
| `SWConditionsNotSatisfied` | `"6985"` | Security or wallet conditions not satisfied (e.g., wallet locked or pending confirmation) |
| `SWSecurityStatusNotSatisfied` | `"6982"` | Security conditions not met |
| `SWWrongLength` | `"6700"` | Incorrect length parameter in APDU frame |
| `SWClassNotSupported` | `"6E00"` | CLA byte not supported |
| `SWInstructionNotSupported` | `"6D00"` | INS byte not recognized |
| `DefaultAID` | `"F00102030405"` | Default proprietary AID for TeknoNFC wallet |

---

## 2. Type Definitions

### `ParsedAPDU`
```go
type ParsedAPDU struct {
    CLA  string
    INS  string
    P1   string
    P2   string
    Lc   int
    Data string
    Le   int
}
```
**File**: `internal/apdu/engine.go:25`  
**Description**: Deconstructed representation of an ISO/IEC 7816-4 command APDU frame.  
- `CLA`: Class byte (hex string, e.g., `"00"`).
- `INS`: Instruction byte (hex string, e.g., `"A4"` for SELECT, `"AE"` for GENERATE AC).
- `P1`: Parameter 1 byte (hex string, e.g., `"04"`).
- `P2`: Parameter 2 byte (hex string, e.g., `"00"`).
- `Lc`: Length of expected incoming data in bytes (integer).
- `Data`: Hexadecimal payload content of length `Lc * 2`.
- `Le`: Maximum length of expected response data bytes.

---

## 3. APDU Engine Functions

### `ParseAPDU`
```go
func ParseAPDU(rawHex string) (*ParsedAPDU, error)
```
**File**: `internal/apdu/engine.go:36`  
**Description**: Parses and decomposes a raw hexadecimal APDU command string into its structured `ParsedAPDU` representation. Strips whitespace, forces uppercase, verifies a minimum length of 8 hex characters (4 bytes for header `CLA-INS-P1-P2`), and dynamically extracts `Lc`, `Data`, and `Le` based on frame length.  
**Parameters**:  
- `rawHex` (`string`): Raw APDU hex string (e.g. `"00A4040006F0010203040500"`).  
**Returns**:  
- `*ParsedAPDU`: Structured APDU object.  
- `error`: Non-nil if the frame is under 8 hex characters or invalid.

### `BuildResponse`
```go
func BuildResponse(dataHex, sw string) string
```
**File**: `internal/apdu/engine.go:88`  
**Description**: Formats an ISO 7816-4 response APDU frame by concatenating the response data payload with the 2-byte hexadecimal Status Word (SW).  
**Parameters**:  
- `dataHex` (`string`): Hex-encoded response body (e.g. FCI template or cryptogram TLV).  
- `sw` (`string`): 4-character hex status word (e.g. `SWSuccess` / `"9000"`).  
**Returns**:  
- `string`: Uppercase concatenated response APDU.

### `ParseBCDAmount`
```go
func ParseBCDAmount(bcdHex string) string
```
**File**: `internal/apdu/engine.go:93`  
**Description**: Converts a 6-byte EMV BCD (Binary Coded Decimal) amount representation (Tag `9F02`, e.g., `"000000002500"`) into a decimal string formatted to 4 decimal places (`"25.0000"`). If decoding fails or amount is non-positive, defaults to `"10.0000"`.  
**Parameters**:  
- `bcdHex` (`string`): 12-character BCD string.  
**Returns**:  
- `string`: Decimal currency string formatted to 4 decimal places.

### `FormatBCDAmount`
```go
func FormatBCDAmount(amountStr string) string
```
**File**: `internal/apdu/engine.go:104`  
**Description**: Encodes a human-readable decimal amount string (e.g. `"25.00"`) into a 12-character (6-byte) zero-padded EMV BCD hex string (e.g. `"000000002500"`).  
**Parameters**:  
- `amountStr` (`string`): Decimal amount string.  
**Returns**:  
- `string`: 12-character BCD hex string.

### `HexToUint64`
```go
func HexToUint64(hexStr string) uint64
```
**File**: `internal/apdu/engine.go:114`  
**Description**: Decodes a hexadecimal string (e.g. `"000D"`) into a `uint64` integer. Used for reading Application Transaction Counters (ATC) and integer lengths. Returns `0` on parsing failure.  
**Parameters**:  
- `hexStr` (`string`): Hexadecimal numeric string.  
**Returns**:  
- `uint64`: Parsed unsigned 64-bit integer.

### `Uint64ToHex2Bytes`
```go
func Uint64ToHex2Bytes(val uint64) string
```
**File**: `internal/apdu/engine.go:123`  
**Description**: Converts an unsigned 64-bit integer into a 2-byte (4 hex characters) zero-padded uppercase hex string (e.g. `13` -> `"000D"`).  
**Parameters**:  
- `val` (`uint64`): Integer value.  
**Returns**:  
- `string`: 4-character hex string.

### `ValidateHex`
```go
func ValidateHex(s string) bool
```
**File**: `internal/apdu/engine.go:128`  
**Description**: Validates that an input string consists entirely of valid hexadecimal byte representations without syntax errors.  
**Parameters**:  
- `s` (`string`): String to validate.  
**Returns**:  
- `bool`: `true` if valid hexadecimal, `false` otherwise.

---

## 4. TLV (Tag-Length-Value) Engine Functions

### `ParseTLV`
```go
func ParseTLV(tlvHex string) map[string]string
```
**File**: `internal/apdu/tlv.go:11`  
**Description**: Parses an EMV BER-TLV (Basic Encoding Rules — Tag-Length-Value) hexadecimal string into a map where keys are uppercase hex tags and values are uppercase hex content strings.  
**Features**:  
- Supports 1-byte tags (e.g. `5A`, `77`).  
- Supports 2-byte tags (e.g. `9F02` for Amount, `9F36` for ATC, `9F37` for Unpredictable Number, `9F26` for ARQC).  
- Supports 1-byte length format (`0x00`-`0x7F`) and multi-byte extended length formats (`0x81`, `0x82`).  
- Skips ISO 7816 padding bytes (`0x00` and `0xFF`).  
**Parameters**:  
- `tlvHex` (`string`): Raw hex TLV stream.  
**Returns**:  
- `map[string]string`: Key-value map of tag to value.

### `BuildTLV`
```go
func BuildTLV(tagHex, valHex string) string
```
**File**: `internal/apdu/tlv.go:81`  
**Description**: Constructs a BER-TLV encoded hexadecimal string given a Tag hex string and a Value hex string. Computes standard BER length encodings:  
- Length < 128: 1 byte (`%02X`).  
- Length <= 255: 2 bytes (`81%02X`).  
- Length > 255: 3 bytes (`82%04X`).  
**Parameters**:  
- `tagHex` (`string`): Hexadecimal tag string (e.g. `"9F02"`).  
- `valHex` (`string`): Hexadecimal value string.  
**Returns**:  
- `string`: Complete uppercase Tag-Length-Value hex string.

---

## 5. Test Functions

### `TestParseSelectAID`
```go
func TestParseSelectAID(t *testing.T)
```
**File**: `internal/apdu/apdu_test.go:7`  
**Description**: Verifies parsing of an ISO/IEC 7816-4 `SELECT AID` command APDU (`00 A4 04 00 06 F00102030405 00`), asserting header correctness (`CLA`, `INS`, `P1`, `P2`), data payload equality, and response frame synthesis via `BuildResponse` with `SWSuccess`.

### `TestParseGenerateAC_TLV`
```go
func TestParseGenerateAC_TLV(t *testing.T)
```
**File**: `internal/apdu/apdu_test.go:28`  
**Description**: Validates parsing of EMV `GENERATE AC` TLV payload containing Tag `9F02` (Amount BCD), Tag `9F36` (ATC), Tag `9F37` (Terminal Unpredictable Number), and Tag `9F26` (Application Cryptogram). Asserts tag extraction, BCD-to-decimal amount parsing via `ParseBCDAmount`, and ATC conversion via `HexToUint64`.

### `TestParseAPDU_ErrorHandling`
```go
func TestParseAPDU_ErrorHandling(t *testing.T)
```
**File**: `internal/apdu/apdu_test.go:57`  
**Description**: Verifies APDU parser error handling against malformed frames: headers shorter than 4 bytes, odd-length hex strings, and invalid non-hexadecimal characters.

