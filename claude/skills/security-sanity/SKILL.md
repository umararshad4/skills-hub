---
name: security-sanity
description: Use when touching auth, sessions, permissions, secrets, payments, user data, database writes, webhooks, or deployment configuration.
---

# Security Sanity

Treat security-sensitive surfaces as high risk.

## Check

- Secrets are not committed or logged.
- Auth/session checks happen on trusted boundaries.
- User-controlled input is validated before privileged use.
- Authorization is separate from authentication.
- Webhook/payment handlers verify signatures.
- Error messages do not leak sensitive internals.

## Verification

Run targeted tests or manual checks for permission boundaries. Use secret scanning for staged diffs.
