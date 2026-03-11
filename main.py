#!/usr/bin/env python3
"""
RAG Social Networks Intelligence Platform - CLI Entry Point
"""
import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.core.db_utils import get_chat_history, insert_application_logs
from src.core.langchain_utils import get_rag_chain
import uuid

load_dotenv()


def main():
    """Interactive CLI for RAG system"""
    print("=" * 60)
    print("🤖 RAG Social Networks Intelligence Platform")
    print("=" * 60)
    print("\nWelcome! Type 'quit' to exit, 'help' for commands.\n")
    
    session_id = str(uuid.uuid4())
    print(f"📊 Session ID: {session_id}\n")
    
    rag_chain = get_rag_chain()
    chat_history = get_chat_history(session_id)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("""
Available commands:
  quit/exit/q  - Exit the application
  help         - Show this help message
  
Ask any question about loaded documents or VK social network analysis!
                """)
                continue
            
            if not user_input:
                continue
            
            print("\n⏳ Processing...")
            
            result = rag_chain.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            answer = result.get("answer", "No response generated.")
            print(f"\n🤖 Assistant: {answer}\n")
            
            # Log to database
            insert_application_logs(session_id, user_input, answer, "cli")
            
            # Update chat history
            chat_history = get_chat_history(session_id)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
