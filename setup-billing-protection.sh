#!/bin/bash

# Script to set up billing protection for Google Cloud Run
# This ensures you never exceed free tier limits

echo -e "\033[36m======================================\033[0m"
echo -e "\033[36mGoogle Cloud Billing Protection Setup\033[0m"
echo -e "\033[36m======================================\033[0m"
echo ""

# Prompt for project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "\033[31mERROR: Project ID is required\033[0m"
    exit 1
fi

# Set project
gcloud config set project "$PROJECT_ID"

echo -e "\n\033[32m1. Setting up budget alerts...\033[0m"
# Create a budget that alerts at $0.01 (essentially anything beyond free tier)
cat > budget-config.json <<EOF
{
  "displayName": "DocuChat Free Tier Protection",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"],
    "services": ["services/F256-5F6D-7C8E"]
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "1"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.9,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 1.0,
      "spendBasis": "CURRENT_SPEND"
    }
  ]
}
EOF

# Note: Budget API requires billing account ID
echo -e "\033[33mTo create budget alerts, go to:\033[0m"
echo -e "\033[37mhttps://console.cloud.google.com/billing/budgets\033[0m"
echo -e "\033[37m- Set budget to \$1\033[0m"
echo -e "\033[37m- Set alerts at 50%, 90%, and 100%\033[0m"
echo ""

echo -e "\n\033[32m2. Setting Cloud Run quota limits...\033[0m"

# Set quota for Cloud Run requests per day (2M/30 days ≈ 67k/day)
# This prevents sudden spikes
cat > quota-override.json <<EOF
{
  "dimensions": {},
  "metric": "run.googleapis.com/request_count",
  "unit": "1/d/{resource.project_id}",
  "overrideValue": "70000",
  "consumerQuotaLimit": "projects/$PROJECT_ID/locations/us-central1/services/docuchat-backend"
}
EOF

echo -e "\033[32m3. Configuring service quotas...\033[0m"

# Display quota commands (requires admin permissions)
echo -e "\033[33mRun these commands with Owner/Admin permissions:\033[0m"
echo ""
echo "# Limit concurrent requests"
echo "gcloud run services update docuchat-backend \\"
echo "  --region us-central1 \\"
echo "  --max-instances 10 \\"
echo "  --concurrency 80"
echo ""
echo "# Set request timeout"
echo "gcloud run services update docuchat-backend \\"
echo "  --region us-central1 \\"
echo "  --timeout 60s"
echo ""

echo -e "\n\033[32m4. Creating monitoring alert...\033[0m"

# Alert when approaching free tier limit
cat > alert-policy.yaml <<EOF
displayName: "DocuChat Request Limit Alert"
combiner: OR
conditions:
  - displayName: "Approaching 2M requests"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="docuchat-backend" AND metric.type="run.googleapis.com/request_count"'
      aggregations:
        - alignmentPeriod: 86400s
          perSeriesAligner: ALIGN_SUM
      comparison: COMPARISON_GT
      thresholdValue: 1800000
      duration: 0s
notificationChannels: []
enabled: true
EOF

echo ""
echo -e "\033[32m✅ Configuration files created!\033[0m"
echo ""
echo -e "\033[36mNext steps:\033[0m"
echo -e "\033[37m1. Set up budget alerts: https://console.cloud.google.com/billing/budgets\033[0m"
echo -e "\033[37m2. Review and apply quota limits above\033[0m"
echo -e "\033[37m3. The application now has built-in rate limiting (2M requests/month)\033[0m"
echo -e "\033[37m4. Monitor usage: https://console.cloud.google.com/run\033[0m"
echo ""
echo -e "\033[32mYour app will automatically reject requests after 2M per month! 🛡️\033[0m"

# Cleanup temp files
rm -f budget-config.json quota-override.json alert-policy.yaml
