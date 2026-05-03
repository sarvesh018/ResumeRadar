#!/bin/bash
# End-to-end smoke test for the full stack
# Run after: docker compose up --build -d
# Usage: bash scripts/test-e2e.sh

set -e

BASE_URL="http://localhost:8080"
PASS=0
FAIL=0

check() {
    local name="$1"
    local expected_code="$2"
    local actual_code="$3"
    if [ "$actual_code" -eq "$expected_code" ]; then
        echo "  ✓ $name (HTTP $actual_code)"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name — expected $expected_code, got $actual_code"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "=========================================="
echo " ResumeRadar E2E Smoke Test"
echo "=========================================="
echo ""

echo "1. Health checks"
check "Gateway" 200 $(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
check "Auth" 200 $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health/live)
check "Profile" 200 $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health/live)
check "Matcher" 200 $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health/live)
check "Tracker" 200 $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/health/live)
check "Analytics" 200 $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8005/health/live)
echo ""

echo "2. Register user"
REGISTER=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@resumeradar.dev","password":"testpassword123","full_name":"Test User"}')
check "Register" 201 $(echo "$REGISTER" | tail -1)
echo ""

echo "3. Login"
LOGIN=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@resumeradar.dev","password":"testpassword123"}')
LOGIN_CODE=$(echo "$LOGIN" | tail -1)
LOGIN_BODY=$(echo "$LOGIN" | head -1)
check "Login" 200 $LOGIN_CODE
TOKEN=$(echo "$LOGIN_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
AUTH="Authorization: Bearer $TOKEN"
echo ""

echo "4. Profile"
check "Get profile" 200 $(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/profile -H "$AUTH")
check "Update profile" 200 $(curl -s -o /dev/null -w "%{http_code}" -X PUT $BASE_URL/api/v1/profile \
    -H "$AUTH" -H "Content-Type: application/json" \
    -d '{"full_name":"Test User","headline":"DevOps Engineer"}')
echo ""

echo "5. Application tracking"
APP=$(curl -s -w "\n%{http_code}" -X POST $BASE_URL/api/v1/applications \
    -H "$AUTH" -H "Content-Type: application/json" \
    -d '{"company":"Google","role_title":"DevOps Engineer","match_score":0.82}')
check "Create app" 201 $(echo "$APP" | tail -1)
APP_ID=$(echo "$APP" | head -1 | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")

if [ -n "$APP_ID" ]; then
    check "Status transition" 200 $(curl -s -o /dev/null -w "%{http_code}" -X PATCH \
        "$BASE_URL/api/v1/applications/$APP_ID/status" \
        -H "$AUTH" -H "Content-Type: application/json" -d '{"status":"screening"}')
    check "Kanban board" 200 $(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/applications/board -H "$AUTH")
    check "Reject invalid transition" 400 $(curl -s -o /dev/null -w "%{http_code}" -X PATCH \
        "$BASE_URL/api/v1/applications/$APP_ID/status" \
        -H "$AUTH" -H "Content-Type: application/json" -d '{"status":"applied"}')
fi
echo ""

echo "6. Analytics"
check "Dashboard" 200 $(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/analytics/dashboard -H "$AUTH")
check "Funnel" 200 $(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/analytics/funnel -H "$AUTH")
echo ""

echo "=========================================="
echo " Results: $PASS passed, $FAIL failed"
echo "=========================================="
echo ""
[ $FAIL -gt 0 ] && exit 1