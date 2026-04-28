#!/bin/bash

API_URL="<http://localhost:8000>"

echo "Testing API endpoints..."
echo ""

echo "1. Testing health check:"
curl -s "$API_URL/test"
echo -e "\n"

echo "2. Creating new AI session:"
curl -s -X POST "$API_URL/ai/new"
echo -e "\n"

echo "3. Getting new session ID and testing chat:"
SESSION_ID=$(curl -s -X POST "$API_URL/ai/new" | grep -o '"session_id": "[^"]*"' | cut -d'"' -f4)
echo "Session ID: $SESSION_ID"

if [ -n "$SESSION_ID" ]; then
    echo "Testing chat with valid session:"
    curl -s -X POST "$API_URL/ai/chat/$SESSION_ID" -H "Content-Type: application/json" -d '{"message": "Hello"}'
    echo -e "\n"
    
    echo "Testing close session:"
    curl -s -X DELETE "$API_URL/ai/close/$SESSION_ID"
    echo -e "\n"
fi

echo "4. Testing chat with invalid session:"
curl -s -X POST "$API_URL/ai/chat/invalid-session" -H "Content-Type: application/json" -d '{"message": "Hello"}'
echo -e "\n"

echo "5. Testing add user:"
curl -s -X POST "$API_URL/users/add" -H "Content-Type: application/json" -d '{"email": "test@example.com", "role": "common_user", "password": "password123"}'
echo -e "\n"

echo "6. Testing login:"
curl -s "$API_URL/users/login" --user "test@example.com:password123"
echo -e "\n"

echo "Done!"
