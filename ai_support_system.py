#!/usr/bin/env python3
"""
AI-Powered GPU Support System
Automates customer support using AI to categorize, prioritize, and respond to GPU-related queries.
"""

import openai
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUSupportAI:
    def __init__(self, openai_api_key: str):
        """Initialize the AI support system."""
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.db_path = "gpu_support.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for support tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                subject TEXT,
                message TEXT,
                category TEXT,
                priority TEXT,
                ai_response TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def categorize_ticket(self, subject: str, message: str) -> Tuple[str, str]:
        """Use AI to categorize and prioritize support tickets."""
        
        prompt = f"""
        Analyze this GPU support ticket and categorize it:
        
        Subject: {subject}
        Message: {message}
        
        Categories: [Installation, Performance, Compatibility, Hardware Issues, Software Bugs, Billing, General]
        Priorities: [Low, Medium, High, Critical]
        
        Respond in JSON format:
        {{
            "category": "category_name",
            "priority": "priority_level",
            "reasoning": "brief explanation"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result["category"], result["priority"]
            
        except Exception as e:
            logger.error(f"Error categorizing ticket: {e}")
            return "General", "Medium"
    
    def generate_response(self, subject: str, message: str, category: str) -> str:
        """Generate AI-powered response for support tickets."""
        
        prompt = f"""
        You are a GPU expert support agent. Respond to this {category} support ticket:
        
        Subject: {subject}
        Message: {message}
        
        Provide a helpful, technical response that:
        1. Acknowledges the user's issue
        2. Provides specific troubleshooting steps
        3. Includes relevant links to documentation
        4. Offers additional resources if needed
        
        Keep the response professional, concise, and actionable.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Thank you for contacting GPU Benchmark Tool support. We're experiencing technical difficulties. Please try again later or contact us directly."
    
    def process_ticket(self, user_email: str, subject: str, message: str) -> Dict:
        """Process a new support ticket with AI."""
        
        # Categorize and prioritize
        category, priority = self.categorize_ticket(subject, message)
        
        # Generate AI response
        ai_response = self.generate_response(subject, message, category)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO support_tickets 
            (user_email, subject, message, category, priority, ai_response)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_email, subject, message, category, priority, ai_response))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Processed ticket #{ticket_id} - Category: {category}, Priority: {priority}")
        
        return {
            "ticket_id": ticket_id,
            "category": category,
            "priority": priority,
            "ai_response": ai_response,
            "status": "processed"
        }
    
    def get_ticket_stats(self) -> Dict:
        """Get statistics about support tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get category distribution
        cursor.execute('SELECT category, COUNT(*) FROM support_tickets GROUP BY category')
        categories = dict(cursor.fetchall())
        
        # Get priority distribution
        cursor.execute('SELECT priority, COUNT(*) FROM support_tickets GROUP BY priority')
        priorities = dict(cursor.fetchall())
        
        # Get resolution time
        cursor.execute('''
            SELECT AVG(julianday(resolved_at) - julianday(created_at)) * 24 
            FROM support_tickets WHERE resolved_at IS NOT NULL
        ''')
        avg_resolution_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "categories": categories,
            "priorities": priorities,
            "avg_resolution_hours": round(avg_resolution_time, 2)
        }

# Example usage
if __name__ == "__main__":
    # Initialize the AI support system
    ai_support = GPUSupportAI("your-openai-api-key-here")
    
    # Example ticket processing
    ticket = ai_support.process_ticket(
        user_email="user@example.com",
        subject="GPU not detected",
        message="My RTX 4090 is not being detected by the benchmark tool. I've updated drivers but still no luck."
    )
    
    print(f"Ticket processed: {ticket}")
    
    # Get statistics
    stats = ai_support.get_ticket_stats()
    print(f"Support stats: {stats}")
