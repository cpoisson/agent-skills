# Observability

Know when something is wrong before your users tell you. This sub-skill covers the minimum viable observability stack for a production web application: structured logging, error tracking, health checks, and post-deploy verification.

## What Observability Gives You

- **Logging** — a record of what happened and when
- **Error tracking** — automatic capture of exceptions and unexpected states
- **Health checks** — a quick yes/no answer to "is the system up and working?"
- **Alerting** — being told about problems rather than discovering them later
- **Post-deploy verification** — confidence that a deploy didn't break anything

## Logging

### What to log

| Event | Level | Data to include |
|-------|-------|----------------|
| Request received | DEBUG (or omit) | Method, path, user ID (no body) |
| Request completed | INFO | Method, path, status code, duration |
| Expected error (user error) | WARN | Error type, request context (no PII) |
| Unexpected error | ERROR | Error message, stack trace, request context |
| Critical failure | FATAL | Full context needed for recovery |
| Auth events | INFO | User ID, event type (login/logout/failure, no passwords) |
| Data mutations | INFO | Resource type, resource ID, user ID |

### What NOT to log

- Passwords, tokens, secrets (ever)
- Full request bodies (may contain PII)
- Full response bodies (may contain sensitive data)
- User PII unless required and consented

### Structured logging format

Use JSON-structured logs so they are parseable by log aggregation tools:

```json
{
  "level": "error",
  "timestamp": "2026-03-25T14:32:01.123Z",
  "message": "Task update failed",
  "requestId": "req_abc123",
  "userId": "usr_456",
  "path": "/api/tasks/789",
  "error": "Foreign key constraint violation",
  "duration": 45
}
```

### Log levels

```
DEBUG  → development only (verbose, usually disabled in prod)
INFO   → normal operation events
WARN   → something unexpected but handled (e.g., rate limit hit)
ERROR  → something broke; requires attention
FATAL  → system cannot continue (rare)
```

In production: INFO and above. In development/staging: DEBUG and above.

## Error Tracking

### Server-side

Capture all unhandled exceptions from your API. At minimum:
- Log the full stack trace to a structured log
- Include enough context to reproduce: request path, user ID, input shape (not value)
- Set up alerts for sustained error rates (e.g., >5 errors/minute)

Recommended tools: Sentry, Highlight.io, Axiom, BetterStack — or just structured ERROR logs shipped to a searchable log service.

### Client-side

Capture JavaScript errors in the browser:

```typescript
// Global error boundary (React)
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary]', error, errorInfo);
    // Send to error tracking service
    captureException(error, { extra: errorInfo });
  }
}

// Global unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  captureException(event.reason);
});

// Global JS errors
window.addEventListener('error', (event) => {
  captureException(event.error);
});
```

### Error rate monitoring

Set a baseline error rate during normal operation. Alert when:
- Error rate exceeds 2× the baseline for more than 5 minutes
- Any FATAL-level error occurs
- Error rate spikes immediately after a deploy

## Health Checks

### Application health endpoint

Every API should expose a health check endpoint:

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "version": "1.2.0",
  "timestamp": "2026-03-25T14:32:01Z"
}
```

- Returns HTTP 200 when healthy
- Returns HTTP 503 when unhealthy (dependency down, etc.)
- Should not require authentication
- Should be fast (< 100ms)

### Deep health check (optional)

A more thorough check that verifies dependencies:

```json
{
  "status": "ok",
  "version": "1.2.0",
  "checks": {
    "database": "ok",
    "storage": "ok"
  }
}
```

Use the deep check for post-deploy verification. Do not expose it publicly if it reveals infrastructure topology.

## Post-Deploy Verification

Run these checks immediately after every production deploy:

```markdown
- [ ] Health check responds 200: `curl https://your-api.example.com/health`
- [ ] Frontend loads without JavaScript errors
- [ ] Primary user flow works (manual spot-check: login → core action)
- [ ] Error tracking shows no new spike in the 5 minutes post-deploy
- [ ] Logs show no unexpected ERROR or FATAL entries
- [ ] Response times are within normal range
```

Automate the first three as a post-deploy smoke test if your CI/CD platform supports it.

## Uptime Monitoring

Set up an external ping to verify the app is reachable from outside your infrastructure:

- Monitor the health check endpoint from an external service
- Alert within 2–3 minutes of downtime
- Lightweight options: BetterStack, UptimeRobot (free tier), Freshping

Alert contacts: who gets notified on downtime? Document this.

## Observability Maturity Checklist

| Capability | Status | Notes |
|------------|--------|-------|
| Structured logs (JSON) | ✅ / ❌ | |
| ERROR logs to searchable store | ✅ / ❌ | |
| Client-side error boundary | ✅ / ❌ | |
| Health check endpoint | ✅ / ❌ | |
| External uptime monitoring | ✅ / ❌ | |
| Post-deploy health check in workflow | ✅ / ❌ | |
| Error rate alerting | ✅ / ❌ | |
| Errors include enough context to reproduce | ✅ / ❌ | |

Score 0–4: Critical gaps — fix before your next production incident.  
Score 5–6: Functional baseline — grow toward alerting and post-deploy automation.  
Score 7–8: Mature — focus on reducing noise and improving signal quality.
