# ♜ GAMBIT Tripartite Brief (Трехсторонний бриф)

> **Status:** `[DRAFT | FROZEN | IMPLEMENTING | VERIFIED]`  
> **Target Delivery Timebox:** 30–60 Minutes  
> **Timestamp:** YYYY-MM-DD HH:MM UTC  
> **Principals:** Grandmaster (Product Owner) · The Rook (Delivery Lead) · Bishop Architect (Systems Lead)

---

## 1. 🎯 MVP Scope (Что входит в спринт)
- [ ] **Core Journey 1:** <User Action -> System Response>
- [ ] **Core Journey 2:** <Data Persistence / Mutation>
- [ ] **Core Journey 3:** <External Integration / Verification>

## 2. ✂️ Anti-Scope (Что безжалостно отрезано ради скорости)
- ❌ *Feature A (Deferred to v2):* <reason>
- ❌ *Feature B (Deferred to v2):* <reason>
- ❌ *Complex edge case (Handled via graceful 400 error):* <reason>

## 3. 🔒 Frozen Interface Contract (`api_contract.json`)
```json
{
  "endpoints": [
    {
      "method": "POST",
      "path": "/api/v1/resource",
      "request_body": {
        "type": "object",
        "required": ["id", "payload"],
        "properties": {
          "id": {"type": "string"},
          "payload": {"type": "object"}
        }
      },
      "response_200": {
        "status": "success",
        "data": {}
      }
    }
  ]
}
```

## 4. ⚖️ 12-Factor & Architecture Alignment
- **Config:** Loaded strictly from environment (`.env` / `pydantic-settings`).
- **Stateless:** Process share-nothing, state in DB/Redis.
- **Port Binding:** Self-contained HTTP service bound to `$PORT`.
- **Disposability:** Instant start, graceful `SIGTERM` shutdown.
- **Healthcheck:** `/healthz` endpoint returning HTTP 200.

## 5. ⚡ Strategic Fork Decision (Вопрос к Grandmaster)
- **Option A (Recommended):** <Description, pros/cons>
- **Option B (Alternative):** <Description, pros/cons>
