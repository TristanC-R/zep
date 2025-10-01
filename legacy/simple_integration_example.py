#!/usr/bin/env python3
"""
Simple Integration Example: Using Zep as a Conversation Database
This shows how to integrate Zep into a simple chat application.
"""

import requests
import json
import uuid
from datetime import datetime
from conversation_database import ZepConversationDB

class SimpleChatApp:
    """A simple chat application using Zep as the conversation database"""
    
    def __init__(self):
        self.db = ZepConversationDB()
        self.current_user = None
        self.current_session = None
    
    def login_user(self, user_id: str, name: str = None, email: str = None):
        """Login or create a user"""
        try:
            # Try to get existing user
            response = requests.get(f"{self.db.base_url}/users/{user_id}", headers=self.db.headers)
            if response.status_code == 200:
                self.current_user = response.json()
                print(f"✅ Welcome back, {self.current_user.get('first_name', user_id)}!")
            else:
                # Create new user
                self.current_user = self.db.create_user(
                    user_id=user_id,
                    email=email or f"{user_id}@example.com",
                    first_name=name or user_id
                )
                print(f"✅ New user created: {name or user_id}")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
        
        return True
    
    def start_conversation(self, topic: str = None):
        """Start a new conversation"""
        if not self.current_user:
            print("❌ Please login first")
            return False
        
        self.current_session = self.db.create_conversation(
            user_id=self.current_user['user_id'],
            metadata={"topic": topic, "started_at": datetime.now().isoformat()}
        )
        print(f"💬 Started new conversation: {self.current_session}")
        if topic:
            print(f"📝 Topic: {topic}")
        return True
    
    def send_message(self, message: str, role: str = "user"):
        """Send a message in the current conversation"""
        if not self.current_session:
            print("❌ No active conversation. Start one first.")
            return False
        
        try:
            self.db.add_message(
                session_id=self.current_session,
                role=role,
                content=message,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            print(f"✅ Message sent: {message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    def get_conversation_history(self, limit: int = 10):
        """Get recent conversation history"""
        if not self.current_session:
            print("❌ No active conversation")
            return []
        
        try:
            context = self.db.get_conversation_context(self.current_session, last_n=limit)
            return context.get('messages', [])
        except Exception as e:
            print(f"❌ Failed to get history: {e}")
            return []
    
    def get_conversation_summary(self):
        """Get a summary of the current conversation"""
        if not self.current_session:
            print("❌ No active conversation")
            return None
        
        try:
            summary = self.db.get_conversation_summary(self.current_session)
            return summary
        except Exception as e:
            print(f"❌ Failed to get summary: {e}")
            return None
    
    def list_user_conversations(self):
        """List all conversations for the current user"""
        if not self.current_user:
            print("❌ Please login first")
            return []
        
        try:
            conversations = self.db.get_user_conversations(self.current_user['user_id'])
            return conversations
        except Exception as e:
            print(f"❌ Failed to list conversations: {e}")
            return []

def interactive_demo():
    """Interactive demo of the chat application"""
    print("💬 Simple Chat Application with Zep Database")
    print("=" * 50)
    
    app = SimpleChatApp()
    
    # Login
    user_id = input("Enter your user ID: ").strip() or f"user-{uuid.uuid4().hex[:8]}"
    name = input("Enter your name (optional): ").strip()
    email = input("Enter your email (optional): ").strip()
    
    if not app.login_user(user_id, name, email):
        return
    
    while True:
        print("\n" + "="*50)
        print("Commands:")
        print("1. Start conversation")
        print("2. Send message")
        print("3. View history")
        print("4. Get summary")
        print("5. List conversations")
        print("6. Exit")
        
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            topic = input("Enter conversation topic (optional): ").strip() or None
            app.start_conversation(topic)
        
        elif choice == "2":
            if not app.current_session:
                print("❌ Start a conversation first")
                continue
            
            message = input("Enter your message: ").strip()
            if message:
                app.send_message(message)
                
                # Simulate an AI response
                if message.lower().startswith(("hello", "hi", "hey")):
                    app.send_message("Hello! How can I help you today?", "assistant")
                elif "help" in message.lower():
                    app.send_message("I'm here to help! What do you need assistance with?", "assistant")
                elif "thank" in message.lower():
                    app.send_message("You're welcome! Is there anything else I can help with?", "assistant")
                else:
                    app.send_message("I understand. Can you tell me more about that?", "assistant")
        
        elif choice == "3":
            history = app.get_conversation_history()
            if history:
                print("\n📜 Conversation History:")
                for i, msg in enumerate(history[-5:], 1):  # Show last 5 messages
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    timestamp = msg.get('metadata', {}).get('timestamp', 'unknown')
                    print(f"  {i}. [{role.upper()}] {content}")
                    print(f"     Time: {timestamp}")
            else:
                print("No conversation history available")
        
        elif choice == "4":
            summary = app.get_conversation_summary()
            if summary:
                print(f"\n📊 Conversation Summary:")
                print(f"   - Session ID: {summary['session_id']}")
                print(f"   - Message count: {summary['message_count']}")
                print(f"   - Facts: {len(summary['relevant_facts'])}")
                print(f"   - Last updated: {summary['last_updated']}")
            else:
                print("No summary available")
        
        elif choice == "5":
            conversations = app.list_user_conversations()
            if conversations:
                print(f"\n📚 Your Conversations ({len(conversations)}):")
                for i, conv in enumerate(conversations, 1):
                    topic = conv.get('metadata', {}).get('topic', 'No topic')
                    created = conv.get('created_at', 'Unknown date')
                    print(f"  {i}. {conv['session_id']} - {topic} ({created})")
            else:
                print("No conversations found")
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def automated_demo():
    """Automated demo showing the chat application in action"""
    print("🤖 Automated Chat Application Demo")
    print("=" * 40)
    
    app = SimpleChatApp()
    
    # Login
    user_id = f"demo-user-{uuid.uuid4().hex[:8]}"
    app.login_user(user_id, "Demo User", "demo@example.com")
    
    # Start conversation
    app.start_conversation("Technical Support")
    
    # Simulate a conversation
    conversation = [
        "Hi, I'm having trouble with my account",
        "I can't access my dashboard",
        "I'm getting a 404 error when I try to log in",
        "I've tried clearing my cache but it didn't help",
        "Thank you for your help!"
    ]
    
    print("\n💬 Simulating conversation...")
    for message in conversation:
        app.send_message(message)
        
        # Simulate AI responses
        if "trouble" in message.lower() or "can't" in message.lower():
            app.send_message("I'm sorry to hear you're having trouble. Let me help you with that.", "assistant")
        elif "404" in message.lower():
            app.send_message("A 404 error usually means the page doesn't exist. Let me check your account status.", "assistant")
        elif "cache" in message.lower():
            app.send_message("Good troubleshooting step! Let me try a different approach to resolve this.", "assistant")
        elif "thank" in message.lower():
            app.send_message("You're welcome! I've reset your account permissions. Try logging in again now.", "assistant")
    
    # Show results
    print("\n📊 Conversation Results:")
    summary = app.get_conversation_summary()
    if summary:
        print(f"   - Messages: {summary['message_count']}")
        print(f"   - Facts: {len(summary['relevant_facts'])}")
    
    conversations = app.list_user_conversations()
    print(f"   - Total conversations: {len(conversations)}")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Interactive demo")
    print("2. Automated demo")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        interactive_demo()
    elif choice == "2":
        automated_demo()
    else:
        print("Invalid choice. Running automated demo...")
        automated_demo()

