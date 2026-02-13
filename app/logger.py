"""
Conversation Logger for Jupiter Edge+ Agent
Logs all interactions for analysis and fine-tuning
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter

class ConversationLogger:
    """Logger for tracking all chat interactions"""
    
    def __init__(self, log_dir: str = "app/data/logs"):
        """
        Initialize the conversation logger
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.jsonl_file = self.log_dir / "chat_interactions.jsonl"
        self.csv_file = self.log_dir / "chat_log.csv"
        
        # Initialize CSV if it doesn't exist
        if not self.csv_file.exists():
            self._initialize_csv()
        
        print(f"📝 Logger initialized: {self.log_dir}")
    
    def _initialize_csv(self):
        """Initialize CSV file with headers"""
        headers = [
            "timestamp", "user_id", "conversation_id", "message_number",
            "user_message", "user_intent", "agent_response", "agent_state",
            "model", "language", "fomo_triggered", "response_time_ms"
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def log_interaction(
        self,
        user_id: str,
        conversation_id: str,
        message_number: int,
        user_message: str,
        user_intent: str,
        agent_response: str,
        agent_state: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a single interaction
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            message_number: Message sequence number
            user_message: User's message
            user_intent: Detected intent
            agent_response: Agent's response
            agent_state: Current agent state
            metadata: Additional metadata
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message_number": message_number,
            "user_message": user_message,
            "user_intent": user_intent,
            "agent_response": agent_response,
            "agent_state": agent_state,
            "metadata": metadata or {}
        }
        
        # Write to JSONL
        try:
            with open(self.jsonl_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️ Warning: Failed to write to JSONL: {e}")
        
        # Write to CSV
        try:
            csv_row = {
                "timestamp": timestamp,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_number": message_number,
                "user_message": user_message[:200],  # Truncate for CSV
                "user_intent": user_intent,
                "agent_response": agent_response[:200],  # Truncate for CSV
                "agent_state": agent_state,
                "model": metadata.get("model", "") if metadata else "",
                "language": metadata.get("language", "") if metadata else "",
                "fomo_triggered": metadata.get("fomo_triggered", False) if metadata else False,
                "response_time_ms": metadata.get("response_time_ms", 0) if metadata else 0,
            }
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_row.keys())
                writer.writerow(csv_row)
        except Exception as e:
            print(f"⚠️ Warning: Failed to write to CSV: {e}")
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        if not self.jsonl_file.exists():
            return []
        
        try:
            with open(self.jsonl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last N lines
            recent_lines = lines[-limit:]
            return [json.loads(line) for line in recent_lines]
        except Exception as e:
            print(f"⚠️ Error reading logs: {e}")
            return []
    
    def get_logs_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific user"""
        if not self.jsonl_file.exists():
            return []
        
        try:
            with open(self.jsonl_file, 'r', encoding='utf-8') as f:
                all_logs = [json.loads(line) for line in f]
            
            return [log for log in all_logs if log.get("user_id") == user_id]
        except Exception as e:
            print(f"⚠️ Error reading logs: {e}")
            return []
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        if not self.jsonl_file.exists():
            return {"message": "No logs available yet"}
        
        try:
            with open(self.jsonl_file, 'r', encoding='utf-8') as f:
                all_logs = [json.loads(line) for line in f]
            
            if not all_logs:
                return {"message": "No logs available yet"}
            
            # Calculate metrics
            total_interactions = len(all_logs)
            unique_users = len(set(log.get("user_id") for log in all_logs))
            unique_conversations = len(set(log.get("conversation_id") for log in all_logs))
            
            # Intent distribution
            intents = [log.get("user_intent") for log in all_logs if log.get("user_intent")]
            intent_counts = Counter(intents)
            
            # Language distribution
            languages = [log.get("metadata", {}).get("language") for log in all_logs]
            language_counts = Counter([lang for lang in languages if lang])
            
            # FOMO trigger rate
            fomo_triggered = sum(1 for log in all_logs if log.get("metadata", {}).get("fomo_triggered"))
            fomo_rate = (fomo_triggered / total_interactions * 100) if total_interactions > 0 else 0
            
            # Average response time
            response_times = [log.get("metadata", {}).get("response_time_ms", 0) for log in all_logs]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "unique_conversations": unique_conversations,
                "intent_distribution": dict(intent_counts.most_common(10)),
                "language_distribution": dict(language_counts),
                "fomo_trigger_rate": f"{fomo_rate:.1f}%",
                "avg_response_time_ms": f"{avg_response_time:.0f}",
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error generating analytics: {e}")
            return {"error": str(e)}
    
    def export_for_finetuning(self, output_file: Optional[str] = None) -> str:
        """
        Export logs in format suitable for LLM fine-tuning (OpenAI format)
        
        Returns:
            Path to the exported file
        """
        if output_file is None:
            output_file = self.log_dir / f"finetuning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        if not self.jsonl_file.exists():
            raise FileNotFoundError("No logs available to export")
        
        try:
            with open(self.jsonl_file, 'r', encoding='utf-8') as f:
                all_logs = [json.loads(line) for line in f]
            
            # Convert to fine-tuning format
            finetuning_data = []
            for log in all_logs:
                # OpenAI fine-tuning format
                entry = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful AI assistant for Jupiter Edge+ Credit Card applications."
                        },
                        {
                            "role": "user",
                            "content": log.get("user_message", "")
                        },
                        {
                            "role": "assistant",
                            "content": log.get("agent_response", "")
                        }
                    ],
                    "metadata": {
                        "intent": log.get("user_intent"),
                        "state": log.get("agent_state"),
                        "language": log.get("metadata", {}).get("language")
                    }
                }
                finetuning_data.append(entry)
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                for entry in finetuning_data:
                    f.write(json.dumps(entry) + '\n')
            
            return str(output_file)
        except Exception as e:
            raise Exception(f"Failed to export fine-tuning data: {e}")
    
    def export_csv(self) -> str:
        """Export logs as CSV (already done during logging)"""
        return str(self.csv_file)
    
    def clear_logs(self):
        """Clear all logs - use with caution!"""
        try:
            if self.jsonl_file.exists():
                self.jsonl_file.unlink()
            if self.csv_file.exists():
                self.csv_file.unlink()
                self._initialize_csv()
            print("✅ All logs cleared")
        except Exception as e:
            print(f"⚠️ Error clearing logs: {e}")
