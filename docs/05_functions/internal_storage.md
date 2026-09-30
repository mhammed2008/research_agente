# TeknoNFC — Function Encyclopedia: Storage & Persistence

> **Module**: `internal/storage`  
> **Source Files**: [`internal/storage/models.go`](file:///d:/teknoKeys/GO-NFC/internal/storage/models.go), [`internal/storage/store.go`](file:///d:/teknoKeys/GO-NFC/internal/storage/store.go), [`internal/storage/sqlite_store.go`](file:///d:/teknoKeys/GO-NFC/internal/storage/sqlite_store.go), [`internal/storage/sqlite_test.go`](file:///d:/teknoKeys/GO-NFC/internal/storage/sqlite_test.go)  
> **Classification**: Zero-Omission Storage Layer Symbol Catalog  

---

## Symbol Manifest

| Symbol Name | Kind | Line Range | Visibility | Description |
| :--- | :--- | :--- | :--- | :--- |
| `User` | Struct | L11 - L34 | Public | Core domain model for user, merchant, and admin accounts |
| `FormattedBalance` | Method | L36 - L45 | Public | Returns balance formatted as 2-decimal currency string |
| `MaskedUID` | Method | L47 - L54 | Public | Returns masked card UID string |
| `MaskedDPAN` | Method | L56 - L63 | Public | Returns masked 16-digit DPAN string |
| `MaskedPhone` | Method | L65 - L72 | Public | Returns masked phone number string |
| `PublicUserResponse` | Struct | L74 - L90 | Public | Sanitized user profile DTO omitting secret keys |
| `ToPublic` | Method | L92 - L102 | Public | Converts `User` struct into `PublicUserResponse` DTO |
| `Transaction` | Struct | L105 - L130 | Public | Double-entry financial transaction record |
| `NfcChallenge` | Struct | L133 - L144 | Public | Cryptographic challenge nonce domain model |
| `IsExpired` | Method | L146 - L155 | Public | Checks if a challenge or transaction confirmation has expired |
| `AdminMetrics` | Struct | L17 - L25 | Public | Aggregated system metrics for super admin dashboard |
| `Store` | Interface | L32 - L65 | Public | Core persistence repository interface |
| `MemoryStore` | Struct | L70 - L82 | Public | Thread-safe in-memory store implementation |
| `NewMemoryStore` | Constructor | L85 - L102 | Public | Factory function initializing `MemoryStore` |
| `getUserMutex` | Method | L104 - L112 | Private | Retrieves or allocates per-user mutex for locking |
| `seedInitialData` | Method | L115 - L205 | Private | Seeds default admin, merchant, and test accounts |
| `persistData` | Method | L207 - L212 | Private | Triggers asynchronous persistence to file |
| `saveToFile` | Method | L214 - L245 | Private | Serializes in-memory state to disk in JSON format |
| `loadFromFile` | Method | L247 - L285 | Private | Restores in-memory state from disk file |
| `SQLiteStore` | Struct | L25 - L27 | Public | Pure Go SQLite storage engine in WAL mode |
| `NewSQLiteStore` | Constructor | L48 - L80 | Public | Opens SQLite database, sets pragmas, and runs migrations |
| `hashPassword` | Function | L23 - L26 | Private | Computes SHA-256 password hash |
| `parseSQLiteTime` | Function | L29 - L46 | Private | Parses datetime strings across RFC3339/SQL layouts |
| `initSchema` | Method | L82 - L205 | Private | Creates tables, triggers migrations, and builds indexes |
| `scanUser` | Method | L270 - L315 | Private | Scans a database row into a `User` struct |
| `getTerminals` | Method | L320 - L340 | Private | Queries all enrolled terminals for a given user ID |
| `scanTx` | Method | L698 - L745 | Private | Scans a database row into a `Transaction` struct |
| `GetUserByID` | Method | Store API | Public | Retrieves user record by integer ID |
| `GetUserByEmail` | Method | Store API | Public | Retrieves user record by unique email address |
| `GetUserByPhone` | Method | Store API | Public | Retrieves user record by E.164 phone number |
| `GetUserByNfcUID` | Method | Store API | Public | Retrieves user by contactless card UID |
| `GetUserByDPAN` | Method | Store API | Public | Retrieves user by 16-digit tokenized DPAN |
| `GetUserByMID` | Method | Store API | Public | Retrieves merchant user by Merchant ID |
| `ResolveUser` | Method | Store API | Public | Smart identifier lookup (by ID, email, phone, DPAN, or MID) |
| `ListUsers` | Method | Store API | Public | Returns all registered users in the system |
| `CreateUser` | Method | Store API | Public | Inserts a new user record |
| `UpdateUser` | Method | Store API | Public | Updates profile fields of an existing user |
| `ActivateMerchant` | Method | Store API | Public | Activates merchant status and assigns new MID |
| `RegisterTerminal` | Method | Store API | Public | Enrolls a new terminal under a merchant |
| `CreateChallenge` | Method | Store API | Public | Stores a newly generated challenge nonce |
| `GetChallenge` | Method | Store API | Public | Retrieves challenge nonce details |
| `MarkChallengeUsed` | Method | Store API | Public | Marks a challenge nonce as consumed |
| `CreateTransaction` | Method | Store API | Public | Inserts a new transaction into the ledger |
| `GetTransactionByID` | Method | Store API | Public | Fetches transaction by primary key ID |
| `GetTransactionByRef` | Method | Store API | Public | Fetches transaction by public UUID reference |
| `ListTransactions` | Method | Store API | Public | Returns recent transactions with limit |
| `ListUserTransactions`| Method | Store API | Public | Returns transactions scoped to a specific user ID |
| `ConfirmTransaction` | Method | Store API | Public | Settles a pending transaction in an atomic ACID transaction |
| `CancelTransaction` | Method | Store API | Public | Cancels a pending transaction and sets failure reason |
| `CountRecentTransactions`| Method | Store API | Public | Counts user transactions within a sliding time window |
| `TransferFunds` | Method | Store API | Public | Atomically transfers balances between two users |
| `AdjustBalance` | Method | Store API | Public | Executes administrative balance adjustments |
| `UpdateUserStatus` | Method | Store API | Public | Updates user account status (active/suspended) |
| `RotateKeys` | Method | Store API | Public | Re-keys user cryptographic credentials |
| `RefundTransaction` | Method | Store API | Public | Issues an administrative refund for a transaction |
| `ReverseTransaction`| Method | Store API | Public | Executes an automated reversal restoring balances |
| `RevokeToken` | Method | Store API | Public | Adds a token to the revoked tokens blacklist |
| `IsTokenRevoked` | Method | Store API | Public | Checks if a session token has been revoked |
| `GetMetrics` | Method | Store API | Public | Aggregates system metrics (users, merchants, volume) |
| `TestSQLiteStoreCompleteSuite` | Test | L10 - L168 | Public | Exhaustive test suite covering SQLite operations |
| `TestSQLiteExistingDatabaseMigration` | Test | L170 - L215 | Public | Validates schema migration against legacy databases |

---

## Detailed Symbol Specifications

### `User`
```go
type User struct {
    ID                int64      `json:"id"`
    Name              string     `json:"name"`
    Email             string     `json:"email"`
    PasswordHash      string     `json:"-"`
    Phone             string     `json:"phone"`
    Role              string     `json:"role"`
    Status            string     `json:"status"`
    Balance           string     `json:"balance"`
    IsMerchant        bool       `json:"is_merchant"`
    MerchantID        string     `json:"merchant_id,omitempty"`
    BusinessName      string     `json:"business_name,omitempty"`
    MCC               string     `json:"mcc,omitempty"`
    Terminals         []Terminal `json:"terminals,omitempty"`
    IsAdmin           bool       `json:"is_admin"`
    NfcCardUID        string     `json:"nfc_card_uid,omitempty"`
    NfcCardMasterKey  string     `json:"-"`
    NfcAuthKey        string     `json:"-"`
    TokenizedDPAN     string     `json:"tokenized_dpan,omitempty"`
    LastATC           uint64     `json:"last_atc"`
    CreatedAt         time.Time  `json:"created_at"`
    UpdatedAt         time.Time  `json:"updated_at"`
}
```
- **Location**: `internal/storage/models.go#L11-L34`
- **Purpose**: Core domain entity representing user profiles, merchant identifiers, cryptographic keys, and ledger balances.

### `FormattedBalance`
```go
func (u *User) FormattedBalance() string
```
- **Location**: `internal/storage/models.go#L36-L45`
- **Purpose**: Returns the account balance formatted to exactly 2 decimal places (e.g. `"250.00"`).

### `PublicUserResponse` & `ToPublic`
```go
type PublicUserResponse struct { ... }
func (u *User) ToPublic() PublicUserResponse
```
- **Location**: `internal/storage/models.go#L74-L102`
- **Purpose**: Safe DTO conversion stripping all sensitive cryptographic keys and password hashes before JSON serialization.

### `Transaction`
```go
type Transaction struct {
    ID                int64      `json:"id"`
    TransactionRef    string     `json:"transaction_ref"`
    SenderID          *int64     `json:"sender_id"`
    ReceiverID        *int64     `json:"receiver_id"`
    AdminID           *int64     `json:"admin_id,omitempty"`
    TerminalID        string     `json:"terminal_id,omitempty"`
    MerchantID        string     `json:"merchant_id,omitempty"`
    IdempotencyKey    string     `json:"idempotency_key,omitempty"`
    Amount            string     `json:"amount"`
    Currency          string     `json:"currency"`
    Type              string     `json:"type"`
    Status            string     `json:"status"`
    ATC               *uint64    `json:"atc,omitempty"`
    Nonce             string     `json:"nonce,omitempty"`
    Cryptogram        string     `json:"cryptogram,omitempty"`
    FailureReason     string     `json:"failure_reason,omitempty"`
    AuditReason       string     `json:"audit_reason,omitempty"`
    RttMs             *int       `json:"rtt_ms,omitempty"`
    ConfirmationToken string     `json:"confirmation_token,omitempty"`
    ConfirmCode       string     `json:"confirm_code,omitempty"`
    ExpiresAt         *time.Time `json:"expires_at,omitempty"`
    CreatedAt         time.Time  `json:"created_at"`
}
```
- **Location**: `internal/storage/models.go#L105-L130`
- **Purpose**: Immutable ledger entry recording debits, credits, timestamps, and audit trails.

### `NfcChallenge` & `IsExpired`
```go
type NfcChallenge struct { ... }
func (c *NfcChallenge) IsExpired() bool
```
- **Location**: `internal/storage/models.go#L133-L155`
- **Purpose**: Tracks 60-second single-use challenge nonces. `IsExpired()` guards against zero-times and normalizes comparisons to UTC.

### `Store` Interface
```go
type Store interface {
    GetUserByID(id int64) (*User, error)
    GetUserByEmail(email string) (*User, error)
    GetUserByPhone(phone string) (*User, error)
    GetUserByNfcUID(uid string) (*User, error)
    GetUserByDPAN(dpan string) (*User, error)
    GetUserByMID(mid string) (*User, error)
    ResolveUser(identifier string) (*User, error)
    ListUsers() ([]*User, error)
    CreateUser(u *User) error
    UpdateUser(u *User) error
    ActivateMerchant(userID int64, businessName, mcc string) (*User, error)
    RegisterTerminal(userID int64, terminalName string) (string, error)
    CreateChallenge(c *NfcChallenge) error
    GetChallenge(nonce string) (*NfcChallenge, error)
    MarkChallengeUsed(nonce string) error
    CreateTransaction(tx *Transaction) error
    GetTransactionByID(id int64) (*Transaction, error)
    GetTransactionByRef(ref string) (*Transaction, error)
    ListTransactions(limit int) ([]*Transaction, error)
    ListUserTransactions(userID int64, limit int) ([]*Transaction, error)
    ConfirmTransaction(txRef, confirmationToken, confirmCode string) (*Transaction, *User, *User, error)
    CancelTransaction(txRef, reason string) (*Transaction, error)
    GetMetrics() (*AdminMetrics, error)
    CountRecentTransactions(senderID int64, window time.Duration) (int, error)
    TransferFunds(senderID, receiverID int64, amount string, newATC uint64, tx *Transaction) error
    AdjustBalance(userID, adminID int64, amount, action, reason string) (*Transaction, *User, error)
    UpdateUserStatus(userID int64, status string) error
    RotateKeys(userID int64, newUID, newKey string) (*User, error)
    RefundTransaction(txRef, reason string) (*Transaction, error)
    ReverseTransaction(txRef, reason string) (*Transaction, error)
    RevokeToken(token string) error
    IsTokenRevoked(token string) bool
}
```
- **Location**: `internal/storage/store.go#L32-L65`
- **Purpose**: Primary repository abstraction fulfilled by both `MemoryStore` and `SQLiteStore`.

### `parseSQLiteTime`
```go
func parseSQLiteTime(s string) time.Time
```
- **Location**: `internal/storage/sqlite_store.go#L29-L46`
- **Purpose**: Robustly parses datetime strings returned by `modernc.org/sqlite` across multiple layouts (RFC3339, RFC3339Nano, ISO8601, and standard SQL datetime), resolving zero-time parsing bugs.

### `ListUserTransactions`
```go
func (s *SQLiteStore) ListUserTransactions(userID int64, limit int) ([]*Transaction, error)
```
- **Location**: `internal/storage/sqlite_store.go#L867-L910`
- **Purpose**: Queries transactions where `sender_id = ? OR receiver_id = ?`, enforcing account isolation and preventing IDOR exposure.

### `ConfirmTransaction`
```go
func (s *SQLiteStore) ConfirmTransaction(txRef, confirmationToken, confirmCode string) (*Transaction, *User, *User, error)
```
- **Location**: `internal/storage/sqlite_store.go#L958-L1085`
- **Purpose**: Executes atomic settlement in SQLite inside `BEGIN IMMEDIATE`. Validates pending state, expiration, and confirmation credentials in constant time before debiting sender and crediting receiver.

### `CancelTransaction`
```go
func (s *SQLiteStore) CancelTransaction(txRef, reason string) (*Transaction, error)
```
- **Location**: `internal/storage/sqlite_store.go#L1089-L1135`
- **Purpose**: Transitions a pending transaction to `CANCELLED` and stores the failure reason.
