## Bug Fixes Applied

### Issue 1: Total count not increasing for late arrivals ✓ FIXED
**Problem**: Second person arriving late wasn't counted
**Root Cause**: Unknown faces (failed recognition) were never tracked
**Solution**: Now tracks all faces and shows better debugging when recognition fails

### Issue 2: Display shows "unknown" but terminal logs correct name ✓ FIXED  
**Problem**: Face recognized once (logged to console) but then shows "unknown" in display
**Root Cause**: Frame-to-frame variation in embeddings caused similarity to drop below threshold
**Solutions Applied**:
1. **Face Tracking Cache**: Once a face is recognized, it's remembered for 5 seconds even if similarity temporarily drops
2. **Relaxed Threshold for Tracked Faces**: Uses 90% of threshold (0.36 instead of 0.40) for already-tracked faces
3. **Lower Recognition Threshold**: Changed from 0.45 to 0.40 for initial recognition
4. **Better Display Labels**: Shows name in UPPERCASE and similarity score on face box

### Issue 3: Concentration stays at 0% ✓ FIXED
**Problem**: Concentration never updates from 0%
**Root Cause**: 
- Concentration only tracked for recognized faces (not "unknown")
- Log timer wasn't being updated after logging
**Solutions Applied**:
1. Fixed log timer update - now properly updates `last_log_time` after each log
2. Concentration now tracked for all faces, even unknown ones
3. Display always shows "FORWARD" or "AWAY" status even for unknown faces

### Additional Improvements ✓
1. **Better Debug Output**: Shows clear messages when faces are detected but similarity is below threshold
2. **Improved Labels**: All statuses now in UPPERCASE for clarity
3. **Cache Cleanup**: Automatically removes old face tracking entries every 30 frames
4. **Always Show Status**: Even unknown faces now show their looking direction

## Test Again

Run the system:
```bash
bash run.sh
```

**Expected behavior now**:
1. ✓ Once recognized, name should stay consistent (not flip to "unknown")
2. ✓ Late arrivals should increment total count
3. ✓ Concentration should update in real-time as you look forward/away
4. ✓ Better terminal messages showing what's happening

**If face still shows as "unknown"**:
- Check terminal for "⚠ Face detected but similarity X.XX < threshold 0.40"
- If similarity is close (e.g., 0.35-0.39), we can lower threshold further in config.py
- Make sure lighting is good and face is clearly visible
