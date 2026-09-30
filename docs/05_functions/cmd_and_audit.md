# Command-Line Binaries & Static Audit Tool Reference

This document catalogs the entry points, command-line interfaces, and static analysis inspection tools of TeknoNFC in `cmd/server` and `cmd/audit`.

---

## 1. Production Server Daemon (`cmd/server/main.go`)

### `main`
```go
func main()
```
**File**: `cmd/server/main.go:19`  
**Description**: Primary entry point for the TeknoNFC payment gateway and admin portal server daemon.  
**Execution Lifecycle**:
1. **Environment Configuration**: Inspects `PORT` (defaults to `"8888"`) and `SQLITE_DB` (defaults to `"data/teknonfc.db"`).
2. **Storage Initialization**: Instantiates `storage.NewSQLiteStore` with pure Go SQLite in WAL (Write-Ahead Logging) mode.
3. **Ledger Service**: Bootstraps `ledger.NewLedgerService` with monotonic ATC enforcement and RTT (Round-Trip Time) bounds checking.
4. **Embedded Static Assets**: Initializes `web.StaticFS()` for serving the single-page admin portal and NFC simulator dashboard.
5. **HTTP Server & Router**: Initializes `api.NewRouter` with CORS, security headers, rate limiting, and route hierarchies.
6. **Graceful Shutdown**: Spawns an HTTP listener in a goroutine and traps `os.Interrupt` and `syscall.SIGTERM` signals. On termination, performs a clean shutdown with a 5-second context timeout to preserve ledger integrity.

---

## 2. Bank-Grade FinTech Static Analysis Auditor (`cmd/audit/main.go`)

The `cmd/audit` package provides an on-demand Abstract Syntax Tree (AST) scanner designed to enforce bank-grade Go engineering standards and prevent financial vulnerabilities (floating point money, side-channel timing attacks, swallowed errors, and naked panics).

### Type Definitions

#### `AuditFinding`
```go
type AuditFinding struct {
    File        string
    Line        int
    Severity    Severity
    Title       string
    Explanation string
    LaravelNote string
    Snippet     string
}
```
**File**: `cmd/audit/main.go:35`  
**Description**: Encapsulates an architectural or security flaw identified by the AST analyzer during source file scanning.  
- `File`: Path to the scanned Go source file.  
- `Line`: Line number of the AST token trigger.  
- `Severity`: Audit severity level (`SevCritical`, `SevWarning`, `SevPass`).  
- `Title`: Short descriptive title of the finding.  
- `Explanation`: Deep-dive technical explanation of why this pattern is unsafe in financial code.  
- `LaravelNote`: Educational bridge explaining the equivalent concept and best practices in PHP/Laravel.  
- `Snippet`: Extracted source code fragment displaying the violation.

---

### Audit Engine Functions

#### `main`
```go
func main()
```
**File**: `cmd/audit/main.go:45`  
**Description**: CLI entry point for the static analysis audit tool. Walks the specified directory (`internal` by default, or an argument passed via CLI), parses each Go source file into an AST using `go/parser` and `go/token`, and runs all four rule checkers across every node using `ast.Inspect`. Evaluates the total findings and prints a colorized terminal report, calculating a FinTech Readiness Score from 0 to 100.

#### `checkFloatingPointCurrency`
```go
func checkFloatingPointCurrency(n ast.Node, fset *token.FileSet, path string, findings *[]AuditFinding)
```
**File**: `cmd/audit/main.go:190`  
**Description**: Inspects AST struct field declarations (`*ast.Field`). If a field name contains financial keywords (`balance`, `amount`, `liquidity`) and uses floating-point types (`float32` or `float64`), appends a `SevWarning` finding to `findings`.  
**Rationale**: IEEE 754 floating-point numbers suffer from precision drift (e.g., `0.1 + 0.2 != 0.3`). Financial ledgers require fixed-point string representations or 64-bit integer cents.  
**Laravel Bridge**: Equivalent to replacing PHP `float` with `bcadd()` / `bcmul()` or Laravel `decimal(18, 4)` database columns.

#### `checkTimingAttackComparisons`
```go
func checkTimingAttackComparisons(n ast.Node, fset *token.FileSet, path string, findings *[]AuditFinding)
```
**File**: `cmd/audit/main.go:218`  
**Description**: Analyzes binary comparison expressions (`*ast.BinaryExpr` with `==` or `!=`). If either operand references sensitive cryptographic tokens (`cryptogram`, `arqc`, `sdmmac`, `sessionkey`, `authkey`, `cmac`) and the comparison is not against a trivial literal (`""`, `0`, `nil`), appends a `SevCritical` finding.  
**Rationale**: Standard equality checks terminate at the first differing byte, enabling adversaries to deduce secret keys or cryptograms byte-by-byte via timing measurements. Enforces `subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1`.  
**Laravel Bridge**: Equivalent to using `hash_equals($known, $user)` instead of `===` in PHP.

#### `checkSwallowedErrors`
```go
func checkSwallowedErrors(n ast.Node, fset *token.FileSet, path string, findings *[]AuditFinding)
```
**File**: `cmd/audit/main.go:269`  
**Description**: Inspects assignment statements (`*ast.AssignStmt`). Detects if the blank identifier `_` is used on the left-hand side to discard errors returned by critical service calls (`Store.*`, `Ledger.*`, `Sign*`, `Verify*`). If found, appends a `SevWarning` finding.  
**Rationale**: Discarding errors in banking software leads to silent desynchronization, phantom transactions, or unverified cryptograms.  
**Laravel Bridge**: In Laravel, unhandled exceptions trigger 500 error handlers and Sentry alerts; in Go, discarding an error with `_` causes silent data corruption.

#### `checkNakedPanics`
```go
func checkNakedPanics(n ast.Node, fset *token.FileSet, path string, findings *[]AuditFinding)
```
**File**: `cmd/audit/main.go:296`  
**Description**: Identifies call expressions (`*ast.CallExpr`) targeting the built-in `panic()` function within production code. If detected, appends a `SevCritical` finding.  
**Rationale**: In Go, an unrecovered `panic()` crashes the entire server process for all concurrent users, violating high-availability requirements. Production services must return structured errors.  
**Laravel Bridge**: In PHP, `throw new Exception()` only aborts the current request; in Go, an uncaught panic terminates the entire HTTP daemon.

#### `exprToString`
```go
func exprToString(expr ast.Expr) string
```
**File**: `cmd/audit/main.go:317`  
**Description**: Helper function converting an AST expression (`ast.Ident`, `ast.SelectorExpr`, `ast.CallExpr`) into a string representation for logging and keyword matching.  
**Parameters**:  
- `expr` (`ast.Expr`): Abstract syntax tree expression.  
**Returns**:  
- `string`: Stringified representation of the expression.

#### `printLaravelToGoCheatSheet`
```go
func printLaravelToGoCheatSheet()
```
**File**: `cmd/audit/main.go:330`  
**Description**: Outputs an ANSI-colorized terminal cheat sheet summarizing the mental model shift from Laravel/PHP to Senior Go FinTech architecture:  
1. *Persistence in Memory*: Daemon lifecycle and `sync.RWMutex` vs. per-request PHP script execution.  
2. *Error Handling*: Explicit `(Result, error)` returns vs. `try/catch` exceptions.  
3. *Concurrency*: Goroutines and channels vs. Redis background queues (`queue:work`).  
4. *Security*: Constant-time comparisons and explicit memory zeroization.
