# TeknoNFC — Function Encyclopedia: API & Controllers

> **Module**: `internal/api`  
> **Source Files**: [`router.go`](file:///d:/teknoKeys/GO-NFC/internal/api/router.go), [`response.go`](file:///d:/teknoKeys/GO-NFC/internal/api/response.go), [`auth_handlers.go`](file:///d:/teknoKeys/GO-NFC/internal/api/auth_handlers.go), [`nfc_handlers.go`](file:///d:/teknoKeys/GO-NFC/internal/api/nfc_handlers.go), [`wallet_handlers.go`](file:///d:/teknoKeys/GO-NFC/internal/api/wallet_handlers.go), [`merchant_handlers.go`](file:///d:/teknoKeys/GO-NFC/internal/api/merchant_handlers.go), [`admin_handlers.go`](file:///d:/teknoKeys/GO-NFC/internal/api/admin_handlers.go), [`api_test.go`](file:///d:/teknoKeys/GO-NFC/internal/api/api_test.go)  
> **Classification**: Zero-Omission HTTP Controllers & Routing Symbol Catalog  

---

## Symbol Manifest

| Symbol Name | Kind | Line Range | Visibility | Description |
| :--- | :--- | :--- | :--- | :--- |
| `RouterConfig` | Struct | `router.go#L13-L17` | Public | Dependency injection configuration for HTTP router |
| `NewRouter` | Constructor | `router.go#L20-L95` | Public | Builds and binds HTTP multiplexer with all routes |
| `Response` | Struct | `response.go#L8-L14` | Public | Unified JSON API envelope format |
| `DeriveErrorCode` | Function | `response.go#L18-L62` | Public | Maps HTTP status and error string to machine-readable error code |
| `WriteJSON` | Function | `response.go#L64-L71` | Public | Serializes and streams JSON responses with status codes |
| `WriteErrorCode` | Function | `response.go#L73-L84` | Public | Standardized JSON error response writer with explicit code |
| `WriteError` | Function | `response.go#L86-L90` | Public | Standardized JSON error response writer |
| `WriteSuccess` | Function | `response.go#L33-L39` | Public | Standardized JSON success response writer |
| `AuthHandler` | Struct | `auth_handlers.go#L17-L19` | Public | Authentication and session controller |
| `NewAuthHandler` | Constructor | `auth_handlers.go#L21-L23` | Public | Instantiates `AuthHandler` |
| `RegisterRequest` | Struct | `auth_handlers.go#L25-L30` | Public | Registration input payload DTO |
| `Register` | Method | `auth_handlers.go#L32-L75` | Public | Handles user registration (`POST /api/auth/register`) |
| `LoginRequest` | Struct | `auth_handlers.go#L77-L80` | Public | Login credentials payload DTO |
| `Login` | Method | `auth_handlers.go#L82-L125`| Public | Authenticates user credentials (`POST /api/auth/login`) |
| `Me` | Method | `auth_handlers.go#L127-L140`| Public | Returns authenticated user profile (`GET /api/auth/me`) |
| `CardProvisioning`| Method | `auth_handlers.go#L142-L175`| Public | Enrolls physical NFC card credentials |
| `Logout` | Method | `auth_handlers.go#L177-L195`| Public | Revokes session token (`POST /api/auth/logout`) |
| `extractAuthUser` | Method | `auth_handlers.go#L197-L215`| Private | Extracts and authenticates Bearer token header |
| `hashPassword` | Function | `auth_handlers.go#L217-L221`| Private | Computes SHA-256 password hash |
| `generateToken` | Function | `auth_handlers.go#L223-L228`| Private | Generates secure bearer session token |
| `NFCHandler` | Struct | `nfc_handlers.go#L17-L20` | Public | Contactless tap and APDU controller |
| `NewNFCHandler` | Constructor | `nfc_handlers.go#L22-L24` | Public | Instantiates `NFCHandler` |
| `ChallengeRequest`| Struct | `nfc_handlers.go#L26-L32` | Public | Challenge generation request DTO |
| `CreateChallenge` | Method | `nfc_handlers.go#L34-L127` | Public | Generates single-use nonce (`POST /api/nfc/challenge`) |
| `PayRequest` | Struct | `nfc_handlers.go#L129-L143`| Public | Contactless tap payload DTO |
| `ProcessTap` | Method | `nfc_handlers.go#L145-L270`| Public | Initiates tap payment (`POST /api/nfc/pay`) |
| `ConfirmPaymentRequest`| Struct | `nfc_handlers.go#L273-L277`| Public | Two-phase confirmation payload DTO |
| `ConfirmPayment` | Method | `nfc_handlers.go#L280-L332`| Public | Confirms payment settlement (`POST /api/nfc/confirm`) |
| `CancelPaymentRequest` | Struct | `nfc_handlers.go#L335-L338`| Public | Payment cancellation payload DTO |
| `CancelPayment` | Method | `nfc_handlers.go#L341-L373`| Public | Cancels pending tap (`POST /api/nfc/cancel`) |
| `CheckPaymentStatus` | Method | `nfc_handlers.go#L376-L450`| Public | Real-time status long-polling (`GET /api/nfc/status`) |
| `StreamPaymentEvents`| Method | `nfc_handlers.go#L453-L505`| Public | Server-Sent Events stream (`GET /api/nfc/events`) |
| `ApduRequest` | Struct | `nfc_handlers.go#L508-L512`| Public | Raw APDU input DTO |
| `ProcessAPDU` | Method | `nfc_handlers.go#L514-L570`| Public | Direct ISO 7816-4 APDU channel (`POST /api/nfc/apdu`) |
| `WalletHandler` | Struct | `wallet_handlers.go#L17-L20`| Public | Wallet operations and ledger query controller |
| `NewWalletHandler`| Constructor | `wallet_handlers.go#L22-L24`| Public | Instantiates `WalletHandler` |
| `requireAdmin` | Method | `wallet_handlers.go#L26-L55`| Private | Guards endpoints requiring super admin role |
| `requireUser` | Method | `wallet_handlers.go#L58-L85`| Private | Extracts authenticated user from session token |
| `ListUsers` | Method | `wallet_handlers.go#L87-L110`| Public | Admin user catalog listing (`GET /api/wallet/users`) |
| `TxDTO` | Struct | `wallet_handlers.go#L112-L130`| Public | User-friendly sanitized transaction response DTO |
| `formatTxDTOs` | Method | `wallet_handlers.go#L132-L158`| Private | Converts transaction models to `TxDTO` slice |
| `ListTransactions`| Method | `wallet_handlers.go#L160-L220`| Public | Ledger queries with IDOR protection |
| `MyTransactions` | Method | `wallet_handlers.go#L223-L251`| Public | User-scoped transaction logs (`GET /api/wallet/my-transactions`) |
| `ConfirmTransaction`| Method | `wallet_handlers.go#L254-L340`| Public | Token-authenticated payment confirmation |
| `TopupRequest` | Struct | `wallet_handlers.go#L343-L346`| Public | Wallet top-up request DTO |
| `Topup` | Method | `wallet_handlers.go#L348-L380`| Public | Adds funds to wallet (`POST /api/wallet/topup`) |
| `ReverseRequest` | Struct | `wallet_handlers.go#L383-L386`| Public | Automated reversal request DTO |
| `ReverseTransaction`| Method | `wallet_handlers.go#L388-L415`| Public | Executes reversal (`POST /api/wallet/transactions/reverse`) |
| `HceProvision` | Method | `wallet_handlers.go#L418-L438`| Public | Provisions HCE profile (`POST /api/wallet/hce/provision`) |
| `MerchantHandler`| Struct | `merchant_handlers.go#L14-L16`| Public | Merchant onboarding controller |
| `NewMerchantHandler`| Constructor | `merchant_handlers.go#L18-L20`| Public | Instantiates `MerchantHandler` |
| `ActivateMerchantRequest`| Struct | `merchant_handlers.go#L22-L26`| Public | Merchant activation DTO |
| `ActivateMerchant`| Method | `merchant_handlers.go#L28-L55`| Public | Activates merchant status |
| `RegisterTerminalRequest`| Struct | `merchant_handlers.go#L58-L61`| Public | Terminal registration DTO |
| `RegisterTerminal`| Method | `merchant_handlers.go#L63-L90`| Public | Enrolls new terminal TID |
| `GetMerchantProfile`| Method | `merchant_handlers.go#L92-L125`| Public | Fetches merchant profile by MID |
| `AdminHandler` | Struct | `admin_handlers.go#L14-L16` | Public | Super admin governance controller |
| `NewAdminHandler`| Constructor | `admin_handlers.go#L18-L20` | Public | Instantiates `AdminHandler` |
| `GetMetrics` | Method | `admin_handlers.go#L28-L45` | Public | Returns system metrics (`GET /api/admin/metrics`) |
| `BalanceAdjustRequest`| Struct | `admin_handlers.go#L48-L53` | Public | Balance adjustment DTO |
| `AdjustBalance` | Method | `admin_handlers.go#L55-L90` | Public | Adjusts user balance |
| `UserStatusRequest`| Struct | `admin_handlers.go#L93-L96` | Public | Account status update DTO |
| `UpdateStatus` | Method | `admin_handlers.go#L98-L125` | Public | Updates user status (active/suspended) |
| `RotateKeysRequest`| Struct | `admin_handlers.go#L128-L130`| Public | Key rotation request DTO |
| `RotateKeys` | Method | `admin_handlers.go#L132-L155`| Public | Rotates user cryptographic keys |
| `RefundRequest` | Struct | `admin_handlers.go#L158-L161`| Public | Refund request DTO |
| `RefundTransaction`| Method | `admin_handlers.go#L163-L190`| Public | Executes administrative refund |
| `setupTestRouter` | Helper | `api_test.go#L17-L26` | Private | Initializes test router with memory store |
| `TestHceProvisioningEndpoint`| Test | `api_test.go#L28-L57` | Public | Tests HCE card profile assignment |
| `TestMerchantActivationAndTerminalRegistration`| Test | `api_test.go#L59-L115` | Public | Tests merchant activation and terminal registration |
| `TestEndToEndPhoneToMerchantTapAndAutoReversal`| Test | `api_test.go#L117-L245`| Public | Tests complete tap, confirmation, and reversal |
| `TestP2PNormalUserToNormalUserTapPayment`| Test | `api_test.go#L247-L305`| Public | Tests peer-to-peer smartphone tap |
| `TestLogoutAndTokenRevocation`| Test | `api_test.go#L307-L365`| Public | Tests session logout and token revocation |
| `TestAdminEndpointsSecurity`| Test | `api_test.go#L367-L460`| Public | Validates admin endpoint security |
| `TestTwoPhasePaymentConfirmationFlow`| Test | `api_test.go#L462-L575`| Public | Tests two-phase confirmation |
| `TestTwoPhasePaymentCancellationFlow`| Test | `api_test.go#L577-L650`| Public | Tests payment cancellation |
| `TestWalletTransactionsUserIsolation`| Test | `api_test.go#L652-L738`| Public | Tests IDOR defenses on transaction logs |
| `TestRealTimeMerchantPaymentStatusNotification`| Test | `api_test.go#L740-L845`| Public | Tests real-time long-polling merchant notification |
| `TestStructuredErrorHandlingAndRecovery`| Test | `api_test.go#L873-L950`| Public | Tests structured error codes, response envelope, and router panic recovery |
| `TestApiNotFoundJsonResponse`| Test | `api_test.go#L952-L983`| Public | Tests JSON 404 response for unmatched API endpoints |
| `mockStaticFS` | Struct | `api_test.go#L985-L989`| Private | Mock static file system for test router |

---

## Detailed Symbol Specifications

### `ProcessTap`
```go
func (h *NFCHandler) ProcessTap(w http.ResponseWriter, r *http.Request)
```
- **Location**: `internal/api/nfc_handlers.go#L145-L270`
- **Purpose**: Processes contactless card and smartphone taps. Enforces two-phase confirmation (`RequireConfirmation: true`, `AutoConfirm: false`), generating a 6-digit confirmation code and UUID token. Zero funds leave the account during this request.
- **Side Effects**: Consumes challenge nonce; inserts `PENDING_CONFIRMATION` record.

### `ConfirmPayment`
```go
func (h *NFCHandler) ConfirmPayment(w http.ResponseWriter, r *http.Request)
```
- **Location**: `internal/api/nfc_handlers.go#L280-L332`
- **Purpose**: Verifies `confirmation_token` or `confirm_code` in constant time, completes ledger settlement, and unblocks waiting POS terminals via `TransactionHub`.

### `CheckPaymentStatus`
```go
func (h *NFCHandler) CheckPaymentStatus(w http.ResponseWriter, r *http.Request)
```
- **Location**: `internal/api/nfc_handlers.go#L376-L450`
- **Purpose**: Implements ultra-fast HTTP long-polling (`&wait=30`) for merchant POS terminals. Holds the connection open using in-memory channels and responds in <50ms when customer confirmation occurs.

### `MyTransactions`
```go
func (h *WalletHandler) MyTransactions(w http.ResponseWriter, r *http.Request)
```
- **Location**: `internal/api/wallet_handlers.go#L223-L251`
- **Purpose**: Returns the authenticated user's own incoming and outgoing transactions. Eliminates cross-account snooping.
