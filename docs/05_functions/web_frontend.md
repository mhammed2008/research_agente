# Web Frontend & Embedded Single-Page Application Reference

This document provides a comprehensive technical reference for the embedded web assets, single-page application (SPA), and JavaScript client runtime engine of the TeknoNFC payment gateway and management dashboard.

---

## 1. Embedded File System (`web/embed.go`)

### `StaticFS`
```go
func StaticFS() (fs.FS, error)
```
**File**: `web/embed.go:12`  
**Description**: Returns an `io/fs.FS` sub-filesystem scoped to the `static` directory, embedded directly into the Go binary at compile-time via `//go:embed static/*`.  
**Returns**:  
- `fs.FS`: File system interface exposing `index.html`, `css/style.css`, and `js/app.js`.  
- `error`: Non-nil if root prefix extraction fails.

---

## 2. JavaScript Enterprise Dashboard Architecture (`web/static/js/app.js`)

The web frontend is a zero-dependency, vanilla ES6 single-page application optimized for bank-grade operations, Arabic RTL (Right-to-Left) typography, and ISO/IEC 7816-4 APDU simulation.

### 2.1 System Lifecycle, Real-Time Clock & Diagnostics

#### `updateClock`
```javascript
function updateClock()
```
**File**: `web/static/js/app.js:14`  
**Description**: Computes and formats the current time in Sana'a (UTC+3) format (`صنعاء HH:MM:SS`) and updates the `#liveClock` DOM element. Invoked immediately and on an interval.

#### `setInterval`
```javascript
setInterval(updateClock, 1000)
```
**File**: `web/static/js/app.js:23`  
**Description**: Native browser timer scheduling periodic invocations of `updateClock` every 1000ms.

#### `showToast`
```javascript
function showToast(message, type = 'info')
```
**File**: `web/static/js/app.js:27`  
**Description**: Displays a transient notification alert (`success`, `error`, `info`) in the top-left notification toast container.

#### `setTimeout`
```javascript
setTimeout(() => { ... }, 4000)
```
**File**: `web/static/js/app.js:36`, `web/static/js/app.js:40`  
**Description**: Controls the lifecycle and smooth fade-out animation of toast elements before DOM removal.

#### `logTerminal`
```javascript
function logTerminal(msg, type = 'info')
```
**File**: `web/static/js/app.js:45`  
**Description**: Appends a timestamped ISO 8601 diagnostics entry into the `#simTerminal` APDU emulator console log, automatically auto-scrolling to the latest entry.

---

### 2.2 Navigation & View Routing

#### `switchNavTab`
```javascript
function switchNavTab(tabId)
```
**File**: `web/static/js/app.js:87`  
**Description**: Manages view switching across dashboard tabs (`tabOverview`, `tabLedger`, `tabAccounts`, `tabMerchants`, `tabSimulator`, `tabSecurity`). Updates active sidebar items and displays the selected tab panel.

---

### 2.3 Authentication & Session Management

#### `getAdminToken`
```javascript
function getAdminToken()
```
**File**: `web/static/js/app.js:122`  
**Description**: Retrieves the active administrator JWT bearer token from browser `sessionStorage`.

#### `setAdminSession`
```javascript
function setAdminSession(token, username)
```
**File**: `web/static/js/app.js:126`  
**Description**: Persists the administrator JWT token and username in `sessionStorage`.

#### `clearAdminSession`
```javascript
function clearAdminSession()
```
**File**: `web/static/js/app.js:131`  
**Description**: Removes admin credentials from `sessionStorage` upon logout or session invalidation.

#### `setAdminView`
```javascript
function setAdminView(isLoggedIn)
```
**File**: `web/static/js/app.js:138`  
**Description**: Toggles DOM visibility between the login modal `#adminLoginModal` and the authenticated dashboard `#appContainer`.

#### `fillDemoAdminCreds`
```javascript
function fillDemoAdminCreds()
```
**File**: `web/static/js/app.js:151`  
**Description**: Populates the login form inputs with default evaluation credentials (`admin` / `Admin@123456`).

#### `checkAdminSession`
```javascript
function checkAdminSession()
```
**File**: `web/static/js/app.js:158`  
**Description**: Evaluates session validity on page load. If an active token exists, triggers data hydration via `refreshAll` and launches `startPolling`.

#### `handleAdminLogin`
```javascript
async function handleAdminLogin(event)
```
**File**: `web/static/js/app.js:189`  
**Description**: Submits administrator credentials to `POST /api/auth/login`. On success, saves session tokens and mounts the portal.

#### `adminLogout`
```javascript
async function adminLogout()
```
**File**: `web/static/js/app.js:255`  
**Description**: Calls `POST /api/auth/logout`, terminates the polling loop via `stopPolling`, clears storage via `clearAdminSession`, and displays the login modal.

#### `authFetch`
```javascript
async function authFetch(url, options = {})
```
**File**: `web/static/js/app.js:276`  
**Description**: Authenticated HTTP wrapper injecting the `Authorization: Bearer <token>` header into API requests. Automatically intercepts `401 Unauthorized` responses to clear sessions and halt background polling.

---

### 2.4 Background Polling & Data Sync

#### `startPolling`
```javascript
function startPolling()
```
**File**: `web/static/js/app.js:299`  
**Description**: Initiates a 5-second recurring polling loop calling `refreshAll` to synchronize real-time ledger metrics.

#### `stopPolling`
```javascript
function stopPolling()
```
**File**: `web/static/js/app.js:305`  
**Description**: Halts the active background polling loop.

#### `clearInterval`
```javascript
clearInterval(pollTimer)
```
**File**: `web/static/js/app.js:307`  
**Description**: Native browser timer cancellation clearing the active `pollTimer` handle.

#### `refreshAll`
```javascript
async function refreshAll()
```
**File**: `web/static/js/app.js:909`  
**Description**: Concurrently invokes `fetchMetrics()`, `fetchUsers()`, and `fetchTransactions()` to refresh all dashboard state.

---

### 2.5 API Retrieval & Data Model Hydration

#### `fetchMetrics`
```javascript
async function fetchMetrics()
```
**File**: `web/static/js/app.js:316`  
**Description**: Calls `GET /api/admin/metrics` to fetch total system liquidity, active user counts, merchant counts, transaction tallies, and relay velocity stats, updating overview counter cards.

#### `fetchUsers`
```javascript
async function fetchUsers()
```
**File**: `web/static/js/app.js:342`  
**Description**: Requests `GET /api/admin/users`, populating `currentUsers` and dispatching rendering calls to `renderUsersTable`, `renderMerchantsTable`, and `populateSimDropdowns`.

#### `fetchTransactions`
```javascript
async function fetchTransactions()
```
**File**: `web/static/js/app.js:464`  
**Description**: Calls `GET /api/admin/transactions` to fetch the global ledger journal, updating `renderTransactionsTable` and `renderRecentTransactionsTable`.

---

### 2.6 Table Rendering & DOM Builders

#### `renderUsersTable`
```javascript
function renderUsersTable(users)
```
**File**: `web/static/js/app.js:358`  
**Description**: Renders customer wallet cards, masked DPANs, current balances, monotonic ATC counters, and action buttons in `#usersTableBody`.

#### `renderMerchantsTable`
```javascript
function renderMerchantsTable(users)
```
**File**: `web/static/js/app.js:401`  
**Description**: Renders registered merchant accounts, business names, MIDs, and active POS terminal IDs in `#merchantsTableBody`.

#### `populateSimDropdowns`
```javascript
function populateSimDropdowns(users)
```
**File**: `web/static/js/app.js:443`  
**Description**: Populates user selection dropdowns in the NFC simulator panel with active wallet accounts.

#### `addTerminalPrompt`
```javascript
async function addTerminalPrompt(userId)
```
**File**: `web/static/js/app.js:425`  
**Description**: Prompts the administrator for a new Terminal Identifier (TID) and calls `POST /api/admin/merchants/terminal` to attach it to a merchant account.

#### `renderTransactionsTable`
```javascript
function renderTransactionsTable(transactions)
```
**File**: `web/static/js/app.js:475`  
**Description**: Generates the complete double-entry ledger journal table with timestamps, reference IDs, sender/receiver names, amounts, and transaction statuses.

#### `renderRecentTransactionsTable`
```javascript
function renderRecentTransactionsTable(transactions)
```
**File**: `web/static/js/app.js:520`  
**Description**: Populates the high-level recent activity stream on the overview dashboard tab.

#### `filterTransactions`
```javascript
function filterTransactions()
```
**File**: `web/static/js/app.js:555`  
**Description**: Filters displayed transactions by search query string (matching reference ID, customer name, or DPAN).

---

### 2.7 Wallet & Account Management

#### `toggleUserStatus`
```javascript
async function toggleUserStatus(userId, currentStatus)
```
**File**: `web/static/js/app.js:577`  
**Description**: Sends `POST /api/admin/users/status` to toggle wallet status between `active` and `suspended`.

#### `rotateUserKeys`
```javascript
async function rotateUserKeys(userId)
```
**File**: `web/static/js/app.js:600`  
**Description**: Calls `POST /api/admin/users/rotate-keys` to trigger cryptographic key rotation, generating new AES-128 MDK secrets.

#### `refundTx`
```javascript
async function refundTx(referenceId)
```
**File**: `web/static/js/app.js:623`  
**Description**: Initiates `POST /api/admin/transactions/refund` to execute an automated reversal and restitution of funds.

#### `openBalanceModal`
```javascript
function openBalanceModal(userId, username, currentBalance)
```
**File**: `web/static/js/app.js:648`  
**Description**: Displays the modal dialog `#balanceModal` to credit or debit an account.

#### `closeBalanceModal`
```javascript
function closeBalanceModal()
```
**File**: `web/static/js/app.js:662`  
**Description**: Hides the balance adjustment modal.

#### `submitBalanceAdjust`
```javascript
async function submitBalanceAdjust(event)
```
**File**: `web/static/js/app.js:667`  
**Description**: Submits a manual balance adjustment to `POST /api/admin/users/adjust-balance`.

#### `openMerchantModal`
```javascript
function openMerchantModal(userId, username)
```
**File**: `web/static/js/app.js:701`  
**Description**: Displays `#merchantModal` for elevating a user to merchant status.

#### `closeMerchantModal`
```javascript
function closeMerchantModal()
```
**File**: `web/static/js/app.js:712`  
**Description**: Closes the merchant onboarding modal dialog.

#### `submitActivateMerchant`
```javascript
async function submitActivateMerchant(event)
```
**File**: `web/static/js/app.js:717`  
**Description**: Dispatches `POST /api/admin/merchants/activate` to provision a merchant entity with MID and initial TID.

---

### 2.8 Contactless NFC & APDU Simulator Engine

#### `simGenerateChallenge`
```javascript
async function simGenerateChallenge()
```
**File**: `web/static/js/app.js:751`  
**Description**: Calls `POST /api/nfc/challenge` to request a fresh 32-bit cryptographically secure unpredictable number (nonce) with a 60-second TTL.

#### `computeClientCryptogram`
```javascript
async function computeClientCryptogram(mdkHex, atc, nonceHex, amountStr)
```
**File**: `web/static/js/app.js:787`  
**Description**: Simulates the client-side smartcard/HCE cryptographic core in JavaScript using the Web Crypto API (`crypto.subtle`), deriving session keys via AES-128-ECB and computing the 8-byte ARQC cryptogram over ATC, Nonce, and Amount.

#### `simExecuteTap`
```javascript
async function simExecuteTap()
```
**File**: `web/static/js/app.js:804`  
**Description**: Orchestrates an automated end-to-end contactless tap simulation:  
1. Obtains a challenge nonce via `POST /api/nfc/challenge`.  
2. Derives card session keys and computes client ARQC.  
3. Submits `POST /api/nfc/pay` with masked DPAN, ATC, Nonce, Amount, and ARQC.  
4. Displays transaction confirmation and updates the live ledger.

#### `simSendAPDU`
```javascript
async function simSendAPDU()
```
**File**: `web/static/js/app.js:862`  
**Description**: Sends a raw hexadecimal ISO 7816-4 APDU frame (`SELECT AID` or `GENERATE AC`) to `POST /api/nfc/apdu` and prints parsed status words and TLV responses into the console.

#### `setApduPreset`
```javascript
function setApduPreset(preset)
```
**File**: `web/static/js/app.js:900`  
**Description**: Populates the raw APDU command input with pre-formatted ISO 7816-4 test vectors (`SELECT AID` or `GENERATE AC`).
