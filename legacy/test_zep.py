#!/usr/bin/env python3
"""
Test script for Zep Community Edition
Tests basic API functionality including user creation, session management, and memory operations.
"""

import requests
import json
import uuid

# Zep API configuration
ZEP_BASE_URL = "http://localhost:8000/api/v2"
API_SECRET = "zep-local-secret-key-12345"

# Headers for API requests
headers = {
    "Authorization": f"Api-Key {API_SECRET}",
    "Content-Type": "application/json"
}

def test_health():
    """Test if Zep API is healthy"""
    print("🔍 Testing Zep API health...")
    response = requests.get("http://localhost:8000/healthz")
    if response.status_code == 200:
        print("✅ Zep API is healthy!")
        return True
    else:
        print(f"❌ Zep API health check failed: {response.status_code}")
        return False

def create_user():
    """Create a test user"""
    print("\n👤 Creating test user...")
    user_data = {
        "user_id": f"test-user-{uuid.uuid4().hex[:8]}",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{ZEP_BASE_URL}/users", headers=headers, json=user_data)
    if response.status_code == 201:
        user = response.json()
        print(f"✅ User created: {user['user_id']}")
        return user['user_id']
    else:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return None

def create_session(user_id):
    """Create a test session"""
    print(f"\n💬 Creating session for user {user_id}...")
    session_data = {
        "user_id": user_id,
        "session_id": f"test-session-{uuid.uuid4().hex[:8]}"
    }
    
    response = requests.post(f"{ZEP_BASE_URL}/sessions", headers=headers, json=session_data)
    if response.status_code == 201:
        session = response.json()
        print(f"✅ Session created: {session['session_id']}")
        return session['session_id']
    else:
        print(f"❌ Failed to create session: {response.status_code} - {response.text}")
        return None

def add_memory(session_id):
    """Add conversation memory to a session"""
    print(f"\n🧠 Adding memory to session {session_id}...")
    memory_data = {
        "messages": [
            {
                "role": "user",
                "role_type": "user",
                "content": "Hi! I'm looking for running shoes. I love Nike."
            },
            {
                "role": "assistant", 
                "role_type": "assistant",
                "content": "Great! I can help you find Nike running shoes. What's your budget?"
            },
            {
                "role": "user",
                "role_type": "user", 
                "content": "Around $100-150. I need them for marathon training."
            },
            {
                "role": "assistant",
                "role_type": "assistant",
                "content": "Perfect! I recommend the Nike Air Zoom Pegasus 40 for $120. It's excellent for marathon training."
            }
        ]
    }
    
    response = requests.post(f"{ZEP_BASE_URL}/sessions/{session_id}/memory", headers=headers, json=memory_data)
    if response.status_code == 201:
        print("✅ Memory added successfully!")
        return True
    else:
        print(f"❌ Failed to add memory: {response.status_code} - {response.text}")
        return False

def get_memory(session_id):
    """Retrieve memory from a session"""
    print(f"\n🔍 Retrieving memory from session {session_id}...")
    response = requests.get(f"{ZEP_BASE_URL}/sessions/{session_id}/memory", headers=headers)
    if response.status_code == 200:
        memory = response.json()
        print("✅ Memory retrieved successfully!")
        print(f"📝 Messages: {len(memory.get('messages', []))}")
        print(f"🧠 Facts: {len(memory.get('relevant_facts', []))}")
        return memory
    else:
        print(f"❌ Failed to retrieve memory: {response.status_code} - {response.text}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Zep Community Edition Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        return
    
    # Test 2: Create user
    user_id = create_user()
    if not user_id:
        return
    
    # Test 3: Create session
    session_id = create_session(user_id)
    if not session_id:
        return
    
    # Test 4: Add memory
    if not add_memory(session_id):
        return
    
    # Test 5: Get memory
    memory = get_memory(session_id)
    if memory:
        print("\n🎉 All tests passed! Zep Community Edition is working correctly.")
        print(f"\n📊 Summary:")
        print(f"   - User ID: {user_id}")
        print(f"   - Session ID: {session_id}")
        print(f"   - Messages stored: {len(memory.get('messages', []))}")
        print(f"   - Facts extracted: {len(memory.get('relevant_facts', []))}")
        
        print(f"\n🌐 Access points:")
        print(f"   - Zep API: http://localhost:8000")
        print(f"   - Neo4j Browser: http://localhost:7474")
        print(f"   - Graphiti Service: http://localhost:8003")
    else:
        print("\n❌ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()
