#!/bin/bash

# Test script om te verifiëren dat alle API endpoints werken
# Dit script test de API endpoints met de juiste API key

BASE_URL="${1:-https://marktplaats-eight.vercel.app}"
API_KEY="${2:-LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=}"

echo "=========================================="
echo "API Endpoint Tests"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "API Key: ${API_KEY:0:10}..."
echo ""

# Test 1: Batch Post Status
echo "Test 1: /api/products/batch-post"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "x-api-key: $API_KEY" \
  "$BASE_URL/api/products/batch-post")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

if [ "$http_code" = "200" ]; then
  echo "✅ SUCCESS (HTTP $http_code)"
  echo "Response: $body"
else
  echo "❌ FAILED (HTTP $http_code)"
  echo "Response: $body"
fi
echo ""

# Test 2: Pending Products
echo "Test 2: /api/products/pending"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "x-api-key: $API_KEY" \
  "$BASE_URL/api/products/pending?api_key=$API_KEY")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

if [ "$http_code" = "200" ]; then
  echo "✅ SUCCESS (HTTP $http_code)"
  product_count=$(echo "$body" | grep -o '"id"' | wc -l | tr -d ' ')
  echo "Products found: $product_count"
else
  echo "❌ FAILED (HTTP $http_code)"
  echo "Response: $body"
fi
echo ""

# Test 3: NextAuth Providers (check if auth works)
echo "Test 3: /api/auth/providers"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  "$BASE_URL/api/auth/providers")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

if [ "$http_code" = "200" ]; then
  echo "✅ SUCCESS (HTTP $http_code)"
  echo "NextAuth is configured"
else
  echo "❌ FAILED (HTTP $http_code)"
  echo "Response: $body"
fi
echo ""

# Test 4: Railway Logs (if configured)
echo "Test 4: /api/railway/logs"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  "$BASE_URL/api/railway/logs")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')

if [ "$http_code" = "200" ]; then
  echo "✅ SUCCESS (HTTP $http_code)"
  echo "Railway logs accessible"
elif [ "$http_code" = "500" ]; then
  echo "⚠️  CONFIGURED BUT ERROR (HTTP $http_code)"
  echo "Response: $body"
  echo "This is expected if RAILWAY_API_TOKEN or RAILWAY_SERVICE_ID is not set"
else
  echo "❌ FAILED (HTTP $http_code)"
  echo "Response: $body"
fi
echo ""

echo "=========================================="
echo "Tests Complete"
echo "=========================================="
