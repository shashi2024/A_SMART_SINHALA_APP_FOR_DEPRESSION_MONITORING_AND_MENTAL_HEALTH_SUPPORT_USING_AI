"""
Batch-based fake user detection service
Analyzes users in batches: 1-5, 15-20, 30-35 chats to detect fake users
Works for both typing and voice patterns
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.firestore_service import FirestoreService

class BatchFakeDetectionService:
    """Service for batch-based fake user detection"""
    
    def __init__(self):
        self.firestore_service = FirestoreService()
        
        # Batch checkpoints for typing analysis
        self.typing_batches = [
            {"start": 1, "end": 5, "name": "initial_batch"},
            {"start": 15, "end": 20, "name": "mid_batch"},
            {"start": 30, "end": 35, "name": "late_batch"}
        ]
        
        # Batch checkpoints for voice analysis
        self.voice_batches = [
            {"start": 1, "end": 5, "name": "initial_batch"},
            {"start": 15, "end": 20, "name": "mid_batch"},
            {"start": 30, "end": 35, "name": "late_batch"}
        ]
    
    def should_check_batch(self, current_count: int, batch_type: str = "typing") -> Optional[Dict[str, Any]]:
        """
        Check if we should analyze a batch based on current message/call count
        
        Args:
            current_count: Current number of chats/calls
            batch_type: "typing" or "voice"
        
        Returns:
            Batch info if checkpoint reached, None otherwise
        """
        batches = self.typing_batches if batch_type == "typing" else self.voice_batches
        
        for batch in batches:
            if batch["start"] <= current_count <= batch["end"]:
                # Check if this is the last message in the batch (end of batch)
                if current_count == batch["end"]:
                    return batch
        
        return None
    
    async def analyze_typing_batch(
        self,
        user_id: str,
        batch_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a batch of typing patterns to detect fake users
        
        Args:
            user_id: User ID
            batch_info: Batch information (start, end, name)
        
        Returns:
            Analysis result with fake score and confidence
        """
        try:
            # Get all typing analyses for this user
            all_analyses = self.firestore_service.get_user_typing_analyses(user_id)
            
            # Sort by creation time to get chronological order
            sorted_analyses = sorted(
                all_analyses,
                key=lambda x: self._get_timestamp(x.get('created_at'))
            )
            
            # Extract batch (1-indexed, so subtract 1 for array indexing)
            batch_start_idx = batch_info["start"] - 1
            batch_end_idx = batch_info["end"]
            
            if len(sorted_analyses) < batch_end_idx:
                return {
                    "batch_name": batch_info["name"],
                    "batch_range": f"{batch_info['start']}-{batch_info['end']}",
                    "actual_count": len(sorted_analyses),
                    "error": "Not enough typing analyses for this batch"
                }
            
            batch_analyses = sorted_analyses[batch_start_idx:batch_end_idx]
            
            # Aggregate features from batch
            aggregated_features = self._aggregate_typing_features(batch_analyses)
            
            # Analyze for fake patterns
            fake_score = self._detect_fake_typing_patterns(aggregated_features)
            
            # Determine if fake
            is_fake = fake_score >= 0.6  # Threshold for fake detection
            
            return {
                "batch_name": batch_info["name"],
                "batch_range": f"{batch_info['start']}-{batch_info['end']}",
                "messages_analyzed": len(batch_analyses),
                "is_fake": is_fake,
                "fake_score": float(fake_score),
                "fake_confidence": float(fake_score),
                "features": aggregated_features,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            print(f"[ERROR] Error analyzing typing batch: {e}")
            import traceback
            traceback.print_exc()
            return {
                "batch_name": batch_info["name"],
                "error": str(e),
                "is_fake": False,
                "fake_score": 0.0
            }
    
    async def analyze_voice_batch(
        self,
        user_id: str,
        batch_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a batch of voice calls to detect fake users
        
        Args:
            user_id: User ID
            batch_info: Batch information (start, end, name)
        
        Returns:
            Analysis result with fake score and confidence
        """
        try:
            # Get all voice analyses for this user
            all_analyses = self.firestore_service.get_user_voice_analyses(user_id)
            
            # Sort by creation time
            sorted_analyses = sorted(
                all_analyses,
                key=lambda x: self._get_timestamp(x.get('created_at'))
            )
            
            # Extract batch
            batch_start_idx = batch_info["start"] - 1
            batch_end_idx = batch_info["end"]
            
            if len(sorted_analyses) < batch_end_idx:
                return {
                    "batch_name": batch_info["name"],
                    "batch_range": f"{batch_info['start']}-{batch_info['end']}",
                    "actual_count": len(sorted_analyses),
                    "error": "Not enough voice analyses for this batch"
                }
            
            batch_analyses = sorted_analyses[batch_start_idx:batch_end_idx]
            
            # Aggregate features from batch
            aggregated_features = self._aggregate_voice_features(batch_analyses)
            
            # Analyze for fake patterns
            fake_score = self._detect_fake_voice_patterns(aggregated_features)
            
            # Determine if fake
            is_fake = fake_score >= 0.6
            
            return {
                "batch_name": batch_info["name"],
                "batch_range": f"{batch_info['start']}-{batch_info['end']}",
                "calls_analyzed": len(batch_analyses),
                "is_fake": is_fake,
                "fake_score": float(fake_score),
                "fake_confidence": float(fake_score),
                "features": aggregated_features,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            print(f"[ERROR] Error analyzing voice batch: {e}")
            import traceback
            traceback.print_exc()
            return {
                "batch_name": batch_info["name"],
                "error": str(e),
                "is_fake": False,
                "fake_score": 0.0
            }
    
    def _aggregate_typing_features(self, batch_analyses: List[Dict]) -> Dict[str, Any]:
        """Aggregate typing features from a batch of analyses"""
        import json
        
        all_timings = []
        typing_speeds = []
        pause_durations = []
        error_rates = []
        
        for analysis in batch_analyses:
            # Extract keystroke timings
            timings_str = analysis.get('keystroke_timings', '[]')
            if isinstance(timings_str, str):
                try:
                    timings = json.loads(timings_str)
                    all_timings.extend(timings)
                except:
                    pass
            elif isinstance(timings_str, list):
                all_timings.extend(timings_str)
            
            # Extract other features
            typing_speeds.append(analysis.get('typing_speed', 0))
            pause_durations.append(analysis.get('pause_duration', 0))
            error_rates.append(analysis.get('error_rate', 0))
        
        # Calculate statistics
        timing_variance = np.var(all_timings) if all_timings else 0
        timing_mean = np.mean(all_timings) if all_timings else 0
        timing_std = np.std(all_timings) if all_timings else 0
        
        avg_typing_speed = np.mean(typing_speeds) if typing_speeds else 0
        std_typing_speed = np.std(typing_speeds) if typing_speeds else 0
        
        avg_pause_duration = np.mean(pause_durations) if pause_durations else 0
        avg_error_rate = np.mean(error_rates) if error_rates else 0
        
        # Consistency metrics (lower variation = more robotic)
        speed_consistency = 1.0 - min(1.0, std_typing_speed / (avg_typing_speed + 1e-6))
        timing_consistency = 1.0 - min(1.0, timing_std / (timing_mean + 1e-6)) if timing_mean > 0 else 0
        
        return {
            "timing_variance": float(timing_variance),
            "timing_mean": float(timing_mean),
            "timing_std": float(timing_std),
            "avg_typing_speed": float(avg_typing_speed),
            "std_typing_speed": float(std_typing_speed),
            "avg_pause_duration": float(avg_pause_duration),
            "avg_error_rate": float(avg_error_rate),
            "speed_consistency": float(speed_consistency),
            "timing_consistency": float(timing_consistency),
            "total_keystrokes": len(all_timings)
        }
    
    def _aggregate_voice_features(self, batch_analyses: List[Dict]) -> Dict[str, Any]:
        """Aggregate voice features from a batch of analyses"""
        import json
        
        pitches = []
        energies = []
        durations = []
        fake_confidences = []
        
        for analysis in batch_analyses:
            pitches.append(analysis.get('pitch', 0))
            energies.append(analysis.get('energy', 0))
            durations.append(analysis.get('duration', 0))
            fake_confidences.append(analysis.get('fake_confidence', 0))
        
        # Calculate statistics
        pitch_variance = np.var(pitches) if pitches else 0
        pitch_mean = np.mean(pitches) if pitches else 0
        energy_variance = np.var(energies) if energies else 0
        energy_mean = np.mean(energies) if energies else 0
        
        # Consistency metrics
        pitch_consistency = 1.0 - min(1.0, np.std(pitches) / (pitch_mean + 1e-6)) if pitch_mean > 0 else 0
        energy_consistency = 1.0 - min(1.0, np.std(energies) / (energy_mean + 1e-6)) if energy_mean > 0 else 0
        
        # Average fake confidence from individual analyses
        avg_fake_confidence = np.mean(fake_confidences) if fake_confidences else 0
        
        return {
            "pitch_variance": float(pitch_variance),
            "pitch_mean": float(pitch_mean),
            "energy_variance": float(energy_variance),
            "energy_mean": float(energy_mean),
            "pitch_consistency": float(pitch_consistency),
            "energy_consistency": float(energy_consistency),
            "avg_duration": float(np.mean(durations)) if durations else 0,
            "avg_fake_confidence": float(avg_fake_confidence),
            "total_calls": len(batch_analyses)
        }
    
    def _detect_fake_typing_patterns(self, features: Dict[str, Any]) -> float:
        """
        Detect fake typing patterns from aggregated features
        Returns fake score (0-1)
        """
        fake_score = 0.0
        
        # 1. Too consistent typing speed (robotic)
        if features["speed_consistency"] > 0.9:
            fake_score += 0.3
        
        # 2. Too consistent timing (robotic)
        if features["timing_consistency"] > 0.85:
            fake_score += 0.25
        
        # 3. Unusually low error rate (too perfect)
        if features["avg_error_rate"] < 0.01:
            fake_score += 0.15
        
        # 4. Unusually consistent pause duration
        if features["avg_pause_duration"] > 0 and features["timing_std"] < 0.1:
            fake_score += 0.1
        
        # 5. Very low timing variance (too regular)
        if features["timing_variance"] < 0.01:
            fake_score += 0.2
        
        return min(1.0, fake_score)
    
    def _detect_fake_voice_patterns(self, features: Dict[str, Any]) -> float:
        """
        Detect fake voice patterns from aggregated features
        Returns fake score (0-1)
        """
        fake_score = 0.0
        
        # 1. Too consistent pitch (synthetic voice)
        if features["pitch_consistency"] > 0.9:
            fake_score += 0.3
        
        # 2. Too consistent energy (synthetic voice)
        if features["energy_consistency"] > 0.85:
            fake_score += 0.25
        
        # 3. Very low pitch variance
        if features["pitch_variance"] < 10:
            fake_score += 0.2
        
        # 4. High fake confidence from individual analyses
        if features["avg_fake_confidence"] > 0.5:
            fake_score += 0.25
        
        return min(1.0, fake_score)
    
    def _get_timestamp(self, timestamp_value) -> datetime:
        """Convert various timestamp formats to datetime"""
        if timestamp_value is None:
            return datetime.min
        
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        
        if hasattr(timestamp_value, 'timestamp'):
            try:
                return datetime.fromtimestamp(timestamp_value.timestamp())
            except:
                pass
        
        if isinstance(timestamp_value, str):
            try:
                return datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
            except:
                pass
        
        return datetime.min
    
    async def get_user_batch_status(
        self,
        user_id: str,
        batch_type: str = "typing"
    ) -> Dict[str, Any]:
        """
        Get status of all batches for a user
        
        Returns:
            Dictionary with batch statuses and overall fake assessment
        """
        try:
            if batch_type == "typing":
                all_analyses = self.firestore_service.get_user_typing_analyses(user_id)
                batches = self.typing_batches
            else:
                all_analyses = self.firestore_service.get_user_voice_analyses(user_id)
                batches = self.voice_batches
            
            total_count = len(all_analyses)
            batch_results = []
            
            for batch in batches:
                if total_count >= batch["end"]:
                    # Batch is complete, analyze it
                    if batch_type == "typing":
                        result = await self.analyze_typing_batch(user_id, batch)
                    else:
                        result = await self.analyze_voice_batch(user_id, batch)
                    batch_results.append(result)
                else:
                    # Batch not yet reached
                    batch_results.append({
                        "batch_name": batch["name"],
                        "batch_range": f"{batch['start']}-{batch['end']}",
                        "status": "pending",
                        "current_count": total_count,
                        "required_count": batch["end"]
                    })
            
            # Overall assessment
            completed_batches = [r for r in batch_results if r.get("is_fake") is not None]
            if completed_batches:
                fake_scores = [r.get("fake_score", 0) for r in completed_batches]
                avg_fake_score = np.mean(fake_scores)
                is_fake_overall = avg_fake_score >= 0.5
            else:
                avg_fake_score = 0.0
                is_fake_overall = False
            
            return {
                "user_id": user_id,
                "batch_type": batch_type,
                "total_count": total_count,
                "batches": batch_results,
                "overall_assessment": {
                    "is_fake": is_fake_overall,
                    "avg_fake_score": float(avg_fake_score),
                    "batches_analyzed": len(completed_batches)
                }
            }
        
        except Exception as e:
            print(f"[ERROR] Error getting batch status: {e}")
            import traceback
            traceback.print_exc()
            return {
                "user_id": user_id,
                "error": str(e)
            }

