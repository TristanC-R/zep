#!/usr/bin/env python3
"""
Zep as a Conversation Database
This script demonstrates how to use Zep as a database for storing and retrieving conversational data and context.
"""

import requests
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

class ZepConversationDB:
    """A wrapper class to use Zep as a conversation database"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v2", api_key: str = "zep-local-secret-key-12345"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_user(self, user_id: str, email: str = None, first_name: str = None, last_name: str = None, metadata: Dict = None) -> Dict:
        """Create a new user in the database"""
        user_data = {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "metadata": metadata or {}
        }
        
        response = requests.post(f"{self.base_url}/users", headers=self.headers, json=user_data)
        response.raise_for_status()
        return response.json()
    
    def create_conversation(self, user_id: str, session_id: str = None, metadata: Dict = None) -> str:
        """Create a new conversation session"""
        if not session_id:
            session_id = f"conv-{uuid.uuid4().hex[:8]}"
        
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "metadata": metadata or {}
        }
        
        response = requests.post(f"{self.base_url}/sessions", headers=self.headers, json=session_data)
        response.raise_for_status()
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> Dict:
        """Add a single message to a conversation"""
        message_data = {
            "messages": [{
                "role": role,
                "role_type": role,
                "content": content,
                "metadata": metadata or {}
            }]
        }
        
        response = requests.post(f"{self.base_url}/sessions/{session_id}/memory", headers=self.headers, json=message_data)
        response.raise_for_status()
        return response.json()
    
    def add_conversation_batch(self, session_id: str, messages: List[Dict]) -> Dict:
        """Add multiple messages to a conversation at once"""
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "role_type": msg["role"],
                "content": msg["content"],
                "metadata": msg.get("metadata", {})
            })
        
        message_data = {"messages": formatted_messages}
        
        response = requests.post(f"{self.base_url}/sessions/{session_id}/memory", headers=self.headers, json=message_data)
        response.raise_for_status()
        return response.json()
    
    def get_conversation_context(self, session_id: str, last_n: int = 10) -> Dict:
        """Get conversation context and relevant facts"""
        response = requests.get(f"{self.base_url}/sessions/{session_id}/memory?lastn={last_n}", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversation sessions for a user"""
        response = requests.get(f"{self.base_url}/users/{user_id}/sessions", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_conversations(self, user_id: str, query: str) -> List[Dict]:
        """Search through user's conversation history"""
        # This would require implementing search functionality
        # For now, we'll get all conversations and filter locally
        conversations = self.get_user_conversations(user_id)
        # In a real implementation, you'd use Zep's search API
        return conversations
    
    def get_conversation_summary(self, session_id: str) -> Dict:
        """Get a summary of the conversation with relevant facts"""
        context = self.get_conversation_context(session_id)
        return {
            "session_id": session_id,
            "message_count": len(context.get("messages", [])),
            "relevant_facts": context.get("relevant_facts", []),
            "context": context.get("context", ""),
            "last_updated": datetime.now().isoformat()
        }

def demo_conversation_database():
    """Demonstrate using Zep as a conversation database"""
    print("🗄️  Zep as a Conversation Database Demo")
    print("=" * 50)
    
    # Initialize the database
    db = ZepConversationDB()
    
    # Create a user
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    print(f"👤 Creating user: {user_id}")
    user = db.create_user(
        user_id=user_id,
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        metadata={"department": "Engineering", "role": "Developer"}
    )
    print(f"✅ User created: {user['user_id']}")
    
    # Create a conversation session
    session_id = db.create_conversation(
        user_id=user_id,
        metadata={"topic": "Technical Support", "priority": "High"}
    )
    print(f"💬 Created conversation: {session_id}")
    
    # Add a conversation about a technical issue
    print("\n📝 Adding conversation about technical issue...")
    conversation = [
        {
            "role": "user",
            "content": "Hi, I'm having trouble with the API integration. The authentication is failing.",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "assistant", 
            "content": "I can help you with the API authentication issue. What error message are you seeing?",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "user",
            "content": "I'm getting a 401 Unauthorized error when trying to authenticate with the API key.",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "assistant",
            "content": "A 401 error usually means the API key is invalid or expired. Let me check your account status and help you generate a new key.",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "user",
            "content": "That would be great. I'm using the key that was generated last week.",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "assistant",
            "content": "I see the issue. Your API key expired yesterday. I've generated a new one for you: sk-new-key-12345. Please update your integration code.",
            "metadata": {"timestamp": datetime.now().isoformat(), "action": "generated_new_key"}
        }
    ]
    
    db.add_conversation_batch(session_id, conversation)
    print("✅ Conversation added successfully!")
    
    # Add another conversation about a different topic
    print("\n📝 Adding conversation about feature request...")
    session_id_2 = db.create_conversation(
        user_id=user_id,
        metadata={"topic": "Feature Request", "priority": "Medium"}
    )
    
    feature_conversation = [
        {
            "role": "user",
            "content": "I'd like to request a new feature for the dashboard. Can we add real-time notifications?",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "assistant",
            "content": "That's a great suggestion! Real-time notifications would improve user experience. What type of notifications are you thinking about?",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "user", 
            "content": "I want to be notified when new data is uploaded, when processing is complete, and when there are any errors.",
            "metadata": {"timestamp": datetime.now().isoformat()}
        },
        {
            "role": "assistant",
            "content": "Perfect! I'll add this to our feature backlog. We can implement WebSocket-based notifications for these events. I'll update you when it's ready for testing.",
            "metadata": {"timestamp": datetime.now().isoformat(), "action": "added_to_backlog"}
        }
    ]
    
    db.add_conversation_batch(session_id_2, feature_conversation)
    print("✅ Feature request conversation added!")
    
    # Retrieve conversation context
    print(f"\n🔍 Retrieving context for session: {session_id}")
    context = db.get_conversation_context(session_id)
    print(f"📊 Context retrieved:")
    print(f"   - Messages: {len(context.get('messages', []))}")
    print(f"   - Facts: {len(context.get('relevant_facts', []))}")
    print(f"   - Context summary: {context.get('context', 'No context available')[:100]}...")
    
    # Get conversation summary
    print(f"\n📋 Conversation Summary for {session_id}:")
    summary = db.get_conversation_summary(session_id)
    print(f"   - Message count: {summary['message_count']}")
    print(f"   - Relevant facts: {len(summary['relevant_facts'])}")
    print(f"   - Last updated: {summary['last_updated']}")
    
    # Get all user conversations
    print(f"\n📚 All conversations for user {user_id}:")
    conversations = db.get_user_conversations(user_id)
    for conv in conversations:
        print(f"   - {conv['session_id']}: {conv.get('metadata', {}).get('topic', 'No topic')}")
    
    print(f"\n🎉 Conversation database demo completed!")
    print(f"📊 Summary:")
    print(f"   - User: {user_id}")
    print(f"   - Conversations: {len(conversations)}")
    print(f"   - Total messages: {sum(len(db.get_conversation_context(conv['session_id']).get('messages', [])) for conv in conversations)}")

if __name__ == "__main__":
    demo_conversation_database()

