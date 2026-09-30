# TeknoNFC — Function Encyclopedia: Ledger & Concurrency Hub

> **Module**: `internal/ledger`  
> **Source Files**: [`internal/ledger/service.go`](file:///d:/teknoKeys/GO-NFC/internal/ledger/service.go), [`internal/ledger/hub.go`](file:///d:/teknoKeys/GO-NFC/internal/ledger/hub.go), [`internal/ledger/ledger_test.go`](file:///d:/teknoKeys/GO-NFC/internal/ledger/ledger_test.go)  
> **Classification**: Zero-Omission Ledger & Event Hub Symbol Catalog  

---

## Symbol Manifest

| Symbol Name | Kind | Line Range | Visibility | Description |
| :--- | :--- | :--- | :--- | :--- |
| `subscriber` | Struct | L9 - L12 | Private | Holds event channel and once guard for single closure |
| `close` | Method | L14 - L18 | Private | Idempotent panic-free channel closing |
| `TransactionHub` | Struct | L21 - L24 | Public | Thread-safe in-memory pub/sub broker for transaction events |
| `NewTransactionHub` | Constructor | L27 - L31 | Public | Initializes a new TransactionHub instance |
| `Subscribe` | Method | L35 - L63 | Public | Registers a subscriber for a specific transaction reference |
| `Publish` | Method | L66 - L90 | Public | Broadcasts updated transaction state to waiting subscribers |
| `LedgerService` | Struct | L16 - L19 | Public | Core transaction orchestration and FinTech rule engine |
| `NewLedgerService` | Constructor | L22 - L27 | Public | Initializes LedgerService with database store and event hub |
| `SubscribeTransaction` | Method | L30 - L32 | Public | Proxies event subscription to the internal TransactionHub |
| `NfcTransferParams` | Struct | L35 - L50 | Public | Parameter DTO for contactless tap authorization |
| `TransferViaNfcAdvanced`| Method | L76 - L286 | Public | Bank-grade contactless payment execution with session KDF |
| `ConfirmPayment` | Method | L289 - L298 | Public | Settles pending transaction and atomically moves funds |
| `CancelPayment` | Method | L301 - L310 | Public | Declines pending payment and releases transaction hold |
| `ReversePayment` | Method | L313 - L322 | Public | Executes atomic transaction reversal for completed payments |
| `CreditFaucet` | Method | L325 - L340 | Public | Test liquidity top-up for sandboxed development wallets |
| `setupTestEnvironment` | Helper | L15 - L65 | Private | Test fixture constructing store, users, and ledger |
| `TestSuccessfulNfcPayment` | Test | L67 - L95 | Public | Tests valid tap authorization and settlement |
| `TestMonotonicityRejection` | Test | L97 - L120 | Public | Validates ATC replay attack rejection |
| `TestRelayAttackRejection` | Test | L122 - L145 | Public | Validates rejection when RTT exceeds 500ms |
| `TestVelocityLimitEnforcement` | Test | L147 - L185 | Public | Validates rate limit (>5 tx/min) account suspension |
| `TestNonceReplayRejection` | Test | L187 - L215 | Public | Validates single-use nonce consumption |
| `TestHceArqcAndMerchantPayment` | Test | L217 - L255 | Public | Tests merchant POS payment with session key derivation |
| `TestHceArqcNormalUserToNormalUserP2P` | Test | L257 - L295 | Public | Tests peer-to-peer smartphone tap payment |
| `TestReversePayment` | Test | L297 - L330 | Public | Validates atomic balance reversal |

---

## Detailed Symbol Specifications

### `subscriber`
```go
type subscriber struct {
    ch   chan *storage.Transaction
    once sync.Once
}
```
- **Location**: `internal/ledger/hub.go#L9-L12`
- **Purpose**: Wraps a transaction notification channel with a `sync.Once` guard to ensure the channel is closed strictly once, eliminating concurrent close panics.

### `close`
```go
func (s *subscriber) close()
```
- **Location**: `internal/ledger/hub.go#L14-L18`
- **Purpose**: Idempotently closes the wrapped subscriber channel using `sync.Once`.

### `TransactionHub`
```go
type TransactionHub struct {
    mu          sync.RWMutex
    subscribers map[string][]*subscriber
}
```
- **Location**: `internal/ledger/hub.go#L21-L24`
- **Purpose**: Thread-safe in-memory pub/sub broker maintaining active client listeners for transaction state changes.

### `NewTransactionHub`
```go
func NewTransactionHub() *TransactionHub
```
- **Location**: `internal/ledger/hub.go#L27-L31`
- **Purpose**: Factory function allocating a new `TransactionHub`.

### `Subscribe`
```go
func (h *TransactionHub) Subscribe(txRef string) (<-chan *storage.Transaction, func())
```
- **Location**: `internal/ledger/hub.go#L35-L63`
- **Purpose**: Subscribes a listener to a specific transaction reference (`txRef`). Returns a receive-only channel and an unsubscribe cleanup closure.
- **Parameters**: `txRef string` — target transaction reference.
- **Return Value**: `(<-chan *storage.Transaction, func())` — Read channel and cleanup callback.

### `Publish`
```go
func (h *TransactionHub) Publish(tx *storage.Transaction)
```
- **Location**: `internal/ledger/hub.go#L66-L90`
- **Purpose**: Dispatches an updated transaction state to all waiting subscribers non-blockingly, then closes the channels and purges the subscription entry.
- **Parameters**: `tx *storage.Transaction` — transaction record with updated status.

### `LedgerService`
```go
type LedgerService struct {
    store storage.Store
    hub   *TransactionHub
}
```
- **Location**: `internal/ledger/service.go#L16-L19`
- **Purpose**: Core financial ledger orchestrator managing double-entry account balances, cryptographic tap verification, velocity limits, and real-time event publishing.

### `NewLedgerService`
```go
func NewLedgerService(store storage.Store) *LedgerService
```
- **Location**: `internal/ledger/service.go#L22-L27`
- **Purpose**: Instantiates `LedgerService` with the specified `Store` and a new `TransactionHub`.

### `SubscribeTransaction`
```go
func (s *LedgerService) SubscribeTransaction(txRef string) (<-chan *storage.Transaction, func())
```
- **Location**: `internal/ledger/service.go#L30-L32`
- **Purpose**: Exposes event subscription capability to API handlers.

### `NfcTransferParams`
```go
type NfcTransferParams struct {
    SenderIdentifier    string
    ReceiverID          int64
    MerchantID          string
    RecipientTag        string
    TerminalID          string
    Amount              string
    Currency            string
    ATC                 uint64
    Nonce               string
    Cryptogram          string
    RttMs               *int
    IdempotencyKey      string
    RequireConfirmation bool
    AutoConfirm         bool
}
```
- **Location**: `internal/ledger/service.go#L35-L50`
- **Purpose**: Comprehensive DTO containing all cryptographic and transactional parameters for a contactless tap transfer.

### `TransferViaNfcAdvanced`
```go
func (s *LedgerService) TransferViaNfcAdvanced(params NfcTransferParams) (*storage.Transaction, *storage.User, *storage.User, error)
```
- **Location**: `internal/ledger/service.go#L76-L286`
- **Purpose**: Primary contactless execution engine. Implements velocity rate limiting (max 5 tx/min), relay timing checks (RTT < 500ms), ATC monotonicity validation, nonce expiration and single-use checks, session key KDF derivation, and constant-time ARQC verification. In two-phase mode, creates a `PENDING_CONFIRMATION` record with zero immediate deduction.

### `ConfirmPayment`
```go
func (s *LedgerService) ConfirmPayment(txRef, confirmationToken, confirmCode string) (*storage.Transaction, *storage.User, *storage.User, error)
```
- **Location**: `internal/ledger/service.go#L289-L298`
- **Purpose**: Validates the customer's confirmation code or token in constant time, atomically debits the sender, credits the receiver, transitions status to `COMPLETED`, and notifies all active listeners on `TransactionHub`.

### `CancelPayment`
```go
func (s *LedgerService) CancelPayment(txRef, reason string) (*storage.Transaction, error)
```
- **Location**: `internal/ledger/service.go#L301-L310`
- **Purpose**: Transitions a pending transaction to `CANCELLED` and notifies listening POS terminals.

### `ReversePayment`
```go
func (s *LedgerService) ReversePayment(txRef string, reason string) (*storage.Transaction, error)
```
- **Location**: `internal/ledger/service.go#L313-L322`
- **Purpose**: Atomically reverses a completed transaction, restoring funds from receiver to sender.

### `CreditFaucet`
```go
func (s *LedgerService) CreditFaucet(userID int64, amount string) (*storage.Transaction, *storage.User, error)
```
- **Location**: `internal/ledger/service.go#L325-L340`
- **Purpose**: Adds test balance funds to development accounts (capped at 10,000.00).

### `setupTestEnvironment`
```go
func setupTestEnvironment() (*LedgerService, storage.Store)
```
- **Location**: `internal/ledger/ledger_test.go#L15-L65`
- **Purpose**: Initializes a test fixture with pre-seeded users (Alice, Bob Merchant) and keys.

### `TestSuccessfulNfcPayment`
```go
func TestSuccessfulNfcPayment(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L67-L95`
- **Purpose**: Validates successful contactless tap payment.

### `TestMonotonicityRejection`
```go
func TestMonotonicityRejection(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L97-L120`
- **Purpose**: Asserts that `incoming ATC <= last recorded ATC` is rejected with a monotonicity security violation.

### `TestRelayAttackRejection`
```go
func TestRelayAttackRejection(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L122-L145`
- **Purpose**: Asserts that `RTT > 500ms` triggers a relay attack decline (`RELAY_SUSPECTED`).

### `TestVelocityLimitEnforcement`
```go
func TestVelocityLimitEnforcement(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L147-L185`
- **Purpose**: Asserts that accounts submitting >5 transactions within 60 seconds are automatically suspended.

### `TestNonceReplayRejection`
```go
func TestNonceReplayRejection(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L187-L215`
- **Purpose**: Asserts that a consumed challenge nonce cannot be re-used.

### `TestHceArqcAndMerchantPayment`
```go
func TestHceArqcAndMerchantPayment(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L217-L255`
- **Purpose**: Validates full HCE session derivation and merchant payment.

### `TestHceArqcNormalUserToNormalUserP2P`
```go
func TestHceArqcNormalUserToNormalUserP2P(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L257-L295`
- **Purpose**: Validates direct smartphone-to-smartphone P2P contactless payment.

### `TestReversePayment`
```go
func TestReversePayment(t *testing.T)
```
- **Location**: `internal/ledger/ledger_test.go#L297-L330`
- **Purpose**: Tests atomic reversal of funds.
