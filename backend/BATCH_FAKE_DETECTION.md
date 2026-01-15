# Batch-Based Fake User Detection System

## Overview

This system detects fake users by analyzing their behavior in batches of chats/calls:
- **Initial Batch**: Chats/Calls 1-5
- **Mid Batch**: Chats/Calls 15-20  
- **Late Batch**: Chats/Calls 30-35

## How It Works

### For Typing Patterns

1. **Individual Chat Analysis**: Each time a user sends a chat message, typing patterns are analyzed:
   - Keystroke timings
   - Typing speed
   - Pause duration
   - Error rate

2. **Batch Checkpoints**: When a user reaches:
   - **5th chat**: Analyzes chats 1-5
   - **20th chat**: Analyzes chats 15-20
   - **35th chat**: Analyzes chats 30-35

3. **Batch Analysis**: For each batch, the system:
   - Aggregates typing features from all chats in the batch
   - Calculates consistency metrics (too consistent = robotic)
   - Detects patterns like:
     - Too consistent typing speed (robotic)
     - Too consistent timing patterns (automated)
     - Unusually low error rate (too perfect)
     - Very low timing variance (too regular)

4. **Fake Score Calculation**:
   - Speed consistency > 0.9: +0.3 fake score
   - Timing consistency > 0.85: +0.25 fake score
   - Error rate < 0.01: +0.15 fake score
   - Timing variance < 0.01: +0.2 fake score
   - **Threshold**: Score >= 0.6 = Fake user

### For Voice Calls

1. **Individual Call Analysis**: Each voice call is analyzed for:
   - Pitch patterns
   - Energy patterns
   - Duration
   - Individual fake confidence

2. **Batch Checkpoints**: Same as typing (5th, 20th, 35th call)

3. **Batch Analysis**: For each batch, the system:
   - Aggregates voice features from all calls in the batch
   - Calculates consistency metrics:
     - Pitch consistency (synthetic voices are too consistent)
     - Energy consistency (flat energy = synthetic)
     - Pitch variance (too low = synthetic)

4. **Fake Score Calculation**:
   - Pitch consistency > 0.9: +0.3 fake score
   - Energy consistency > 0.85: +0.25 fake score
   - Pitch variance < 10: +0.2 fake score
   - High individual fake confidence: +0.25 fake score
   - **Threshold**: Score >= 0.6 = Fake user

## API Endpoints

### Typing Batch Status
```
GET /api/typing/batch-status
```
Returns status of all batches for the current user's typing patterns.

**Response:**
```json
{
  "user_id": "user123",
  "batch_type": "typing",
  "total_count": 25,
  "batches": [
    {
      "batch_name": "initial_batch",
      "batch_range": "1-5",
      "messages_analyzed": 5,
      "is_fake": false,
      "fake_score": 0.3,
      "fake_confidence": 0.3
    },
    {
      "batch_name": "mid_batch",
      "batch_range": "15-20",
      "messages_analyzed": 5,
      "is_fake": true,
      "fake_score": 0.75,
      "fake_confidence": 0.75
    },
    {
      "batch_name": "late_batch",
      "batch_range": "30-35",
      "status": "pending",
      "current_count": 25,
      "required_count": 35
    }
  ],
  "overall_assessment": {
    "is_fake": true,
    "avg_fake_score": 0.525,
    "batches_analyzed": 2
  }
}
```

### Voice Batch Status
```
GET /api/voice/batch-status
```
Returns status of all batches for the current user's voice calls.

## Automatic Detection

The system automatically:
1. **Triggers batch analysis** when a user reaches checkpoint (5th, 20th, 35th chat/call)
2. **Creates alerts** if batch analysis indicates fake user (score >= 0.6)
3. **Combines results** - Uses batch result if available, otherwise individual result
4. **Tracks progress** - Each batch is analyzed independently

## Why Batch Analysis?

1. **Pattern Detection**: Fake users often show consistent patterns across multiple interactions
2. **Reduced False Positives**: Single interactions might be misleading, batches provide better accuracy
3. **Progressive Monitoring**: Early detection (1-5) vs. later patterns (30-35) can show different behaviors
4. **Behavioral Consistency**: Real users show natural variation, fake users show robotic consistency

## Integration Points

### Typing Route (`/api/typing/analyze`)
- Automatically checks for batch checkpoints after saving each typing analysis
- Returns batch analysis results in the response `insights.batch_analysis`

### Voice Route (`/api/voice/analyze`)
- Automatically checks for batch checkpoints after saving each voice analysis
- Combines batch results with individual call bot detection

## Alerts

When a batch indicates a fake user:
- **Alert Type**: `batch_fake_detected`
- **Severity**: 
  - `high` if fake_score >= 0.8
  - `medium` if fake_score >= 0.6
- **Message**: Includes batch name, range, and fake score

## Future Enhancements

1. **Machine Learning Integration**: Use trained models for batch analysis
2. **Adaptive Thresholds**: Adjust thresholds based on user history
3. **Cross-Modal Analysis**: Combine typing and voice batch results
4. **Temporal Patterns**: Analyze how patterns change over time
5. **Custom Batch Ranges**: Allow configuration of batch ranges

