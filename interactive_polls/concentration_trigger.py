#!/usr/bin/env python3
"""
Concentration Monitor with Interactive Activity Trigger
Monitors classroom concentration and triggers engagement activities
"""

import sys
import os
sys.path.append('interactive_polls')

import time
from datetime import datetime
import subprocess
import poll_config as config

class ConcentrationActivityTrigger:
    def __init__(self):
        self.last_trigger_time = 0
        self.in_activity = False
        self.trigger_count = 0
        
    def should_trigger(self, concentration_score):
        """Check if we should trigger an interactive activity"""
        current_time = time.time()
        time_since_last = current_time - self.last_trigger_time
        
        # Don't trigger if already in activity
        if self.in_activity:
            return False
        
        # Don't trigger if not enough time has passed
        if time_since_last < config.MIN_TIME_BETWEEN_ACTIVITIES:
            return False
        
        # Trigger if concentration is low
        if concentration_score < config.CONCENTRATION_THRESHOLD:
            return True
        
        return False
    
    def trigger_activity(self):
        """Launch interactive quiz/poll"""
        print("\n" + "🚨"*30)
        print("CONCENTRATION ALERT!")
        print("🚨"*30)
        print(f"\nClass concentration below {config.CONCENTRATION_THRESHOLD}%")
        print("Launching interactive activity to re-engage students...\n")
        print("="*60)
        
        self.in_activity = True
        self.trigger_count += 1
        
        try:
            # Step 1: Generate quiz
            print("Step 1: Generating quiz from recent lecture content...")
            result = subprocess.run([
                'python3', 'interactive_polls/quiz_generator.py'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Quiz generation failed: {result.stderr}")
                self.in_activity = False
                return False
            
            print("✓ Quiz generated successfully\n")
            
            # Step 2: Start web server (non-blocking)
            print("Step 2: Starting web server for students...")
            print(f"📱 Students can access at: http://{self._get_ip()}:{config.WEB_PORT}")
            print("\n" + "="*60)
            print("⚠️  ACTIVITY RUNNING - Waiting for students to participate")
            print("="*60)
            
            # Launch quiz server in background
            subprocess.Popen([
                'python3', 'interactive_polls/quiz_server.py'
            ])
            
            # Wait for activity duration
            time.sleep(config.QUIZ_DURATION + 10)  # Quiz duration + buffer
            
            print("\n✓ Activity completed!")
            print(f"   Trigger #{self.trigger_count} finished\n")
            
            self.last_trigger_time = time.time()
            self.in_activity = False
            
            # Start cooldown
            print(f"Cooldown: {config.ACTIVITY_COOLDOWN}s before next possible trigger\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during activity: {e}")
            self.in_activity = False
            return False
    
    def _get_ip(self):
        """Get local IP address"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def get_status(self):
        """Get current trigger status"""
        if self.in_activity:
            return "🎮 ACTIVITY IN PROGRESS"
        
        time_since_last = time.time() - self.last_trigger_time
        if time_since_last < config.ACTIVITY_COOLDOWN:
            remaining = int(config.ACTIVITY_COOLDOWN - time_since_last)
            return f"⏸️  COOLDOWN ({remaining}s remaining)"
        
        return "✅ READY"

# Testing
if __name__ == "__main__":
    trigger = ConcentrationActivityTrigger()
    
    print("Testing Concentration Activity Trigger")
    print("="*60)
    
    # Simulate concentration scores
    test_scores = [65, 55, 45, 38, 35, 42, 50, 60]
    
    for score in test_scores:
        print(f"\nClass Concentration: {score}%")
        print(f"Trigger Status: {trigger.get_status()}")
        
        if trigger.should_trigger(score):
            print("→ Triggering activity!")
            trigger.trigger_activity()
        else:
            print("→ No trigger")
        
        time.sleep(2)
