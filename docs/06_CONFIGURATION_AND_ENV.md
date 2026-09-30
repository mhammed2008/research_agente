# Configuration & Environment Specification

This document details all configuration parameters, environment variables, SQLite database pragmas, and cryptographic security thresholds governing the TeknoNFC payment ledger and gateway service.

---

## 1. Environment Variables

The TeknoNFC server daemon (`cmd/server/main.go`) inspects the host environment for runtime configuration at boot:

| Variable | Type | Default Value | Description |
|---|---|---|---|
| `PORT` | `string` (Numeric) | `"8888"` | HTTP TCP port on which the gateway listens for API requests and admin portal traffic. |
| `SQLITE_DB` | `string` (Path) | `"data/teknonfc.db"` | Relative or absolute filesystem path to the persistent SQLite database file. If parent directories do not exist, they are automatically initialized. |
| `ADMIN_PASSWORD` | `string` | `"Admin@123456"` | Root administrative password used to initialize the primary administrator user (`admin`) upon first database bootstrap. |
| `ENVIRONMENT` | `string` | `"production"` | Operational runtime profile (`development`, `staging`, `production`). In production, secure cookie flags and HTTPS headers are enforced. |

---

## 2. SQLite Database Configuration & Pragmas

TeknoNFC uses pure Go SQLite (`modernc.org/sqlite`) running without CGO dependencies. The database connection pool is configured in `internal/storage/sqlite_store.go` with high-concurrency ACID (Atomicity, Consistency, Isolation, Durability) pragmas:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -64000;
```

### Pragma Rationale:
- **`journal_mode = WAL`** (Write-Ahead Logging): Allows simultaneous readers to read from the database without blocking writers, and permits writers to commit transactions without blocking readers.
- **`synchronous = NORMAL`**: Synchronizes the WAL file to disk at critical checkpoints, delivering a 10x throughput improvement over `FULL` while guaranteeing zero corruption on application crashes.
- **`foreign_keys = ON`**: Enforces strict referential integrity across users, terminals, challenges, and transactions.
- **`busy_timeout = 5000`**: Sets a 5,000ms (5-second) lock acquisition timeout before returning `SQLITE_BUSY`, preventing database locked errors under high concurrent transaction volume.
- **`cache_size = -64000`**: Allocates 64MB of memory cache for hot table indexes and account balances.

---

## 3. Cryptographic Security & Anti-Fraud Thresholds

In accordance with PCI DSS v4.0.1 and EMV contactless standards, the following immutable parameters are enforced by `internal/ledger/service.go` and `internal/crypto/nfc_crypto.go`:

| Parameter | Value | Standard / Rule | Description |
|---|---|---|---|
| `ChallengeTTL` | `60 * time.Second` | PCI DSS v4.0.1 | Time-to-live for terminal challenge nonces. Expired nonces are rejected. |
| `MaxContactlessRTT` | `500 * time.Millisecond` | EMV Contactless Rule 10 | Round-Trip Time bound between challenge issuance and payment submission. Requests exceeding 500ms are flagged as `RELAY_SUSPECTED`. |
| `CardVelocityWindow` | `60 * time.Second` | Rule 11 (Velocity Checking) | Sliding window for evaluating card tap frequency. |
| `MaxCardVelocity` | `5 transactions` | Rule 11 | Maximum transactions allowed per card within 60s before declining with `VELOCITY_EXCEEDED`. |
| `TerminalVelocityWindow`| `60 * time.Second` | Rule 11 | Sliding window for evaluating merchant terminal request rates. |
| `MaxTerminalVelocity` | `30 transactions` | Rule 11 | Maximum authorizations allowed per terminal within 60s before flagging `TERMINAL_COMPROMISED`. |
| `AmountAnomalyMultiplier`| `3.0x` | Rule 11 | Multiplier triggering step-up authentication if a single transaction exceeds 3x the 30-day average. |
| `OfflineFloorLimit` | `50,000 YER` | Rule 10 | Maximum offline cumulative balance permitted before requiring online server authorization. |
| `TokenExpiration` | `24 * time.Hour` | Security Policy | Administrative and wallet session JWT token lifetime. |

---

## 4. Key Management & Rotation Guidelines

1. **Master Derivation Keys (MDK)**: Each registered wallet user is provisioned with a 128-bit (16-byte) symmetric AES Master Derivation Key.
2. **Key Storage**: Keys are stored encrypted at rest in the SQLite database.
3. **Runtime Zeroization**: Derived session keys (`SessionKeyEnc`, `SessionKeyMac`) are kept only in local stack byte slices and explicitly zeroized using `subtle.ConstantTimeCompare` memory wipes immediately after cryptogram validation.
4. **On-Demand Key Rotation**: Administrative endpoint `POST /api/admin/users/rotate-keys` provides instant key rotation, generating fresh CSPRNG keys without invalidating the customer's account identity.
