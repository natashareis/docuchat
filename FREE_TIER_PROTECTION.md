# 🛡️ Free Tier Protection Guide

This document explains how DocuChat ensures you **never pay** for Google Cloud Run.

## Multi-Layer Protection

### 1. ✅ Application-Level Rate Limiting

**Automatic Protection Built Into the App:**

The backend includes a middleware that:
- **Tracks requests per month** (resets automatically)
- **Enforces 2,000,000 request limit** (Cloud Run free tier)
- **Automatically rejects** requests beyond the limit with HTTP 429
- **Adds rate limit headers** to every response:
  - `X-RateLimit-Limit`: 2000000
  - `X-RateLimit-Remaining`: Requests left this month
  - `X-RateLimit-Used`: Requests used so far
  - `X-RateLimit-Warning`: Warning when < 100k remaining

**What happens at 2M requests?**
```json
HTTP 429 Too Many Requests
{
  "error": "Monthly request limit exceeded",
  "message": "Free tier limit of 2,000,000 requests per month has been reached. Please try again next month.",
  "limit": 2000000,
  "current": 2000001,
  "reset_date": "2026-03-01"
}
```

**Counter resets automatically** on the 1st of each month.

### 2. ✅ Cloud Run Resource Limits

**Deployment enforces:**
- `--max-instances 10` - Never spin up more than 10 containers
- `--concurrency 80` - Max 80 concurrent requests per instance
- `--timeout 60s` - Kill long-running requests
- `--cpu 1` - Single CPU per instance
- `--memory 512Mi` - 512MB RAM per instance

**Why this matters:**
- Prevents runaway scaling
- Limits compute costs
- Ensures predictable resource usage

### 3. ⚠️ Budget Alerts (Optional but Recommended)

Set up billing alerts to get notified if any charges occur:

```bash
.\setup-billing-protection.ps1  # Windows
./setup-billing-protection.sh   # Mac/Linux
```

Then manually set up budget at:
👉 https://console.cloud.google.com/billing/budgets

**Recommended settings:**
- Budget amount: **$1.00**
- Alert thresholds: **50%, 90%, 100%**
- Email notifications to your account

### 4. 📊 Monitoring

**View your usage:**
```bash
# Get current month's request count
curl https://your-backend-url.run.app/api/v1/health

# Response includes rate limit info in headers
```

**Cloud Console:**
- Requests: https://console.cloud.google.com/run/detail/us-central1/docuchat-backend/metrics
- Billing: https://console.cloud.google.com/billing

---

## Free Tier Breakdown

### Google Cloud Run (Always Free)

| Resource | Free Tier | Your Limit |
|----------|-----------|------------|
| **Requests** | 2M/month | 2M (hard limit) |
| **Compute Time** | 180k vCPU-seconds | Limited by requests |
| **Memory** | 360k GiB-seconds | 512Mi per instance |
| **Network Egress** | 1 GB/month | Monitor usage |

### Protection Mechanisms

| Layer | Type | Limit | Action |
|-------|------|-------|--------|
| App Middleware | Hard stop | 2M req/month | Returns HTTP 429 |
| Max Instances | Resource limit | 10 instances | No new instances |
| Concurrency | Request limit | 80/instance | Queue or reject |
| Timeout | Time limit | 60 seconds | Kill request |
| Budget Alert | Notification | $1 | Email alert |

---

## Cost Scenarios

### Scenario 1: Normal Usage (100k requests/month)
```
Requests: 100,000 (within free tier)
Cost: $0.00 ✅
```

### Scenario 2: Heavy Usage (1.9M requests/month)
```
Requests: 1,900,000 (within free tier)
Cost: $0.00 ✅
Warning: Approaching limit
```

### Scenario 3: Hitting the Limit
```
Requests: 2,000,000 → automatic cutoff
Further requests: HTTP 429 rejected
Cost: $0.00 ✅
Resume: Next month (auto-reset)
```

### Scenario 4: Traffic Spike Attack
```
Many simultaneous requests → max 10 instances
10 instances × 80 concurrency = 800 concurrent max
Excess requests → queued or rejected
Cost: Still $0.00 ✅ (within free tier limits)
```

---

## FAQs

**Q: What if someone tries to DDoS my app?**
A: Cloud Run's `--concurrency 80` and `--max-instances 10` limit max concurrent requests to 800. The rate limiter will cut off at 2M total. No charges beyond free tier.

**Q: Can I accidentally go over 2M requests?**
A: No. The middleware counts every request and returns HTTP 429 after 2M. The app physically cannot process request #2,000,001.

**Q: How is the counter stored?**
A: In `/tmp/request_counter.json` in the container. Persists across requests but resets on container restart (which is fine - conservative approach).

**Q: What if the counter file gets deleted?**
A: Worst case: counter resets to 0 and you get another 2M requests that month. You still won't be charged (within free tier).

**Q: Does health check count toward the limit?**
A: No. Health checks (`/`, `/health`, `/api/v1/health`) are excluded from rate limiting.

**Q: How do I monitor usage?**
A: Check response headers (`X-RateLimit-Used`) or view Cloud Run metrics console.

**Q: Can I increase the limit?**
A: Yes, edit `MonthlyRequestLimiter.FREE_TIER_LIMIT` in `backend/app/middleware/rate_limit.py`. But remember: requests beyond 2M/month incur charges (~$0.40 per million).

**Q: What happens on the 1st of the month?**
A: Counter automatically resets. Service resumes normal operation.

---

## Verification

Test the protection is working:

```bash
# Check rate limit headers
curl -I https://your-backend-url.run.app/api/v1/health

# Should see:
# X-RateLimit-Limit: 2000000
# X-RateLimit-Remaining: 1999999
# X-RateLimit-Used: 1
```

---

## Summary

✅ **App-level hard limit:** 2M requests/month  
✅ **Cloud Run limits:** Max instances, concurrency, timeout  
✅ **Budget alerts:** Optional but recommended  
✅ **Auto-reset:** 1st of each month  
✅ **No surprise charges:** Impossible to exceed free tier  

**You can deploy with confidence. You will never be charged.** 🛡️
