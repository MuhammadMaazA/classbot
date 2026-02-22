#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from dashboard.dashboard_server import read_attendance_stats, read_concentration_stats

print("Current Dashboard Stats:")
print("=" * 50)

attendance = read_attendance_stats()
print(f"\n📊 ATTENDANCE:")
print(f"  Total Students: {attendance['total_students']}")
print(f"  Present: {attendance['present']}")
print(f"  On-time: {attendance['on_time']}")
print(f"  Late: {attendance['late']}")
print(f"  Rate: {attendance['attendance_rate']}%")
print(f"\n  Students:")
for s in attendance['students']:
    print(f"    - {s['name']}: {s['status']} at {s['time']}")

concentration = read_concentration_stats()
print(f"\n🧠 CONCENTRATION:")
print(f"  Average: {concentration['average_concentration']}%")
print(f"  Focused: {concentration['focused_students']}")
print(f"  Distracted: {concentration['distracted_students']}")
print(f"\n  Recent Readings:")
for r in concentration['recent_readings'][:5]:
    print(f"    - {r['name']}: {'FOCUSED' if r['looking_forward'] else 'AWAY'} at {r['timestamp']}")

print("\n" + "=" * 50)
