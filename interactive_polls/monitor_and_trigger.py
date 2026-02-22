#!/usr/bin/env python3
"""
Standalone Concentration Monitor with Activity Trigger
Reads concentration data from classroom monitor and triggers activities
"""

import time
import os
import sys

sys.path.insert(0, 'interactive_polls')
from concentration_trigger import ConcentrationActivityTrigger

def monitor_concentration_log():
    """Monitor concentration from log file"""
    trigger = ConcentrationActivityTrigger()
    log_file = "logs/concentration.csv"
    
    print("="*60)
    print("INTERACTIVE ENGAGEMENT MONITOR")
    print("="*60)
    print(f"Monitoring: {log_file}")
    print(f"Trigger threshold: <{trigger_config.CONCENTRATION_THRESHOLD}%")
    print(f"Cooldown: {trigger_config.MIN_TIME_BETWEEN_ACTIVITIES}s")
    print("="*60)
    print("\nWaiting for classroom monitor to start...\n")
    
    last_check_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Check every 10 seconds
            if current_time - last_check_time < 10:
                time.sleep(1)
                continue
            
            last_check_time = current_time
            
            # Read latest concentration score
            if not os.path.exists(log_file):
                continue
            
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) < 2:  # Need header + at least one data line
                        continue
                    
                    # Get last line
                    last_line = lines[-1].strip()
                    if not last_line:
                        continue
                    
                    # Parse: timestamp,name,looking_forward,looking_away,score
                    parts = last_line.split(',')
                    if len(parts) >= 5:
                        score = float(parts[4])
                        
                        status = trigger.get_status()
                        print(f"[{time.strftime('%H:%M:%S')}] Concentration: {score:.1f}% | Status: {status}")
                        
                        if trigger.should_trigger(score):
                            print("\n" + "!"*60)
                            print("  LOW CONCENTRATION DETECTED!")
                            print("!"*60 + "\n")
                            trigger.trigger_activity()
            
            except Exception as e:
                print(f"Error reading log: {e}")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        print(f"Total triggers: {trigger.trigger_count}")

if __name__ == "__main__":
    # Import config after path is set
    import poll_config as trigger_config
    
    monitor_concentration_log()
