from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict
import re


@dataclass
class TextFeatures:
    token_count: int
    nonsense_ratio: float
    unique_word_ratio: float
    joke_word_count: int
    abuse_word_count: int
    suspicious_words: Set[str] = field(default_factory=set)  # Words that triggered detection
    nonsense_words: Set[str] = field(default_factory=set)    # Nonsense words found
    joke_words_found: Set[str] = field(default_factory=set)   # Joke words found
    abuse_words_found: Set[str] = field(default_factory=set)  # Abuse words found


@dataclass
class BehaviorFeatures:
    call_duration_sec: float
    repeat_call_count_last_hour: int


@dataclass
class FakeCallResult:
    fake_score: float          # final 0–1 fake probability after rules
    risk_label: str            # "low_fake_risk" / "medium_fake_risk" / "high_fake_risk"
    action: str                # suggested action for staff / bot
    text_features: TextFeatures
    behavior_features: BehaviorFeatures
    suspicious_words: List[str] = field(default_factory=list)  # All suspicious words found
    word_contributions: Dict[str, float] = field(default_factory=dict)  # Word -> contribution score


class FakeCallAlgorithm:
    """
    Heuristic layer on top of:
      - fake call ML model (probability)
      - depression detection model (probability)

    You will call `analyze_call(...)` for each call/segment.
    """

    def __init__(
        self,
        joke_words: Optional[List[str]] = None,
        abuse_words: Optional[List[str]] = None,
        high_depression_threshold: float = 0.7,
    ):
        # TODO: extend these with Sinhala / Tamil / local slang words.
        self.joke_words = {w.lower() for w in (joke_words or [
            "prank", "joke", "justkidding", "lol", "lmao", "forfun"
        ])}
        self.abuse_words = {w.lower() for w in (abuse_words or [
            "idiot", "stupid", "fool", "bitch", "fuck"
        ])}
        self.high_depression_threshold = high_depression_threshold

    # ---------- Feature extraction ----------

    def _tokenize(self, text: str) -> List[str]:
        """Very simple tokenizer. Replace with your own if needed."""
        return re.findall(r"\w+", text.lower())

    def extract_text_features(self, transcript: str) -> TextFeatures:
        tokens = self._tokenize(transcript)
        token_count = len(tokens)

        if token_count == 0:
            return TextFeatures(
                token_count=0,
                nonsense_ratio=1.0,
                unique_word_ratio=0.0,
                joke_word_count=0,
                abuse_word_count=0,
                suspicious_words=set(),
                nonsense_words=set(),
                joke_words_found=set(),
                abuse_words_found=set(),
            )

        nonsense_tokens = 0
        joke_word_count = 0
        abuse_word_count = 0
        nonsense_words = set()
        joke_words_found = set()
        abuse_words_found = set()
        suspicious_words = set()

        for t in tokens:
            # Joke / abuse counting (you can add Sinhala/Tamil variants)
            if t in self.joke_words:
                joke_word_count += 1
                joke_words_found.add(t)
                suspicious_words.add(t)

            if t in self.abuse_words:
                abuse_word_count += 1
                abuse_words_found.add(t)
                suspicious_words.add(t)

            # Nonsense detection heuristics
            alpha_chars = sum(c.isalpha() for c in t)
            alpha_ratio = alpha_chars / len(t)

            has_long_repeat = bool(re.search(r"(.)\1\1\1", t))  # 4 same chars in a row, e.g. "aaaa"

            is_nonsense = (
                len(t) > 20            # unrealistically long
                or alpha_ratio < 0.5   # many digits/symbols
                or has_long_repeat
            )

            if is_nonsense:
                nonsense_tokens += 1
                nonsense_words.add(t)
                suspicious_words.add(t)

        nonsense_ratio = nonsense_tokens / token_count
        unique_word_ratio = len(set(tokens)) / token_count

        return TextFeatures(
            token_count=token_count,
            nonsense_ratio=nonsense_ratio,
            unique_word_ratio=unique_word_ratio,
            joke_word_count=joke_word_count,
            abuse_word_count=abuse_word_count,
            suspicious_words=suspicious_words,
            nonsense_words=nonsense_words,
            joke_words_found=joke_words_found,
            abuse_words_found=abuse_words_found,
        )

    def make_behavior_features(
        self,
        call_duration_sec: float,
        repeat_call_count_last_hour: int,
    ) -> BehaviorFeatures:
        """Simple wrapper so structure is clear & extendable later."""
        return BehaviorFeatures(
            call_duration_sec=float(call_duration_sec),
            repeat_call_count_last_hour=int(repeat_call_count_last_hour),
        )

    # ---------- Scoring & decision ----------

    def combine_scores(
        self,
        p_fake_model: float,
        text_features: TextFeatures,
        behavior_features: BehaviorFeatures,
        depression_score: Optional[float] = None,
    ) -> FakeCallResult:
        """
        Combine:
          - p_fake_model      (from your fake-call ML model, 0–1)
          - depression_score  (from depression model, 0–1, optional)
          - text & behavior features

        into a final fake_score and recommended action.
        """
        fake_score = float(p_fake_model)
        word_contributions = {}
        suspicious_words_list = []

        # Track base model score contribution
        word_contributions["base_model_score"] = p_fake_model

        # 1) Boost for nonsense when depression is low or not provided
        if depression_score is None or depression_score < 0.3:
            nonsense_boost = 0.2 * min(1.0, text_features.nonsense_ratio / 0.4)
            if nonsense_boost > 0:
                fake_score += nonsense_boost
                word_contributions["nonsense_patterns"] = nonsense_boost
                suspicious_words_list.extend(list(text_features.nonsense_words))

        # 2) Low content: many tokens but very low vocabulary richness
        if text_features.token_count > 20 and text_features.unique_word_ratio < 0.3:
            fake_score += 0.1
            word_contributions["low_vocabulary_richness"] = 0.1

        # 3) Jokes & abuse
        if text_features.joke_word_count >= 3:
            fake_score += 0.1
            word_contributions["joke_words"] = 0.1
            suspicious_words_list.extend(list(text_features.joke_words_found))
        elif text_features.joke_word_count > 0:
            # Even single joke words are suspicious
            suspicious_words_list.extend(list(text_features.joke_words_found))

        if text_features.abuse_word_count >= 3:
            fake_score += 0.15
            word_contributions["abuse_words"] = 0.15
            suspicious_words_list.extend(list(text_features.abuse_words_found))
        elif text_features.abuse_word_count > 0:
            # Even single abuse words are suspicious
            suspicious_words_list.extend(list(text_features.abuse_words_found))

        # 4) Short, repeated calls from the same number
        if (
            behavior_features.call_duration_sec < 15
            and behavior_features.repeat_call_count_last_hour >= 3
        ):
            fake_score += 0.2
            word_contributions["suspicious_behavior"] = 0.2

        # 5) Safety: if depression is high, never mark as high fake risk
        if depression_score is not None and depression_score >= self.high_depression_threshold:
            original_score = fake_score
            fake_score = min(fake_score, 0.3)
            adjustment = fake_score - original_score
            if adjustment < 0:
                word_contributions["depression_safety_adjustment"] = adjustment

        # Clamp to [0, 1]
        fake_score = max(0.0, min(1.0, fake_score))

        # Map to label + suggested action (for admin panel / triage)
        if fake_score >= 0.7:
            risk_label = "high_fake_risk"
            action = "flag_for_staff_review_low_priority"
        elif fake_score >= 0.4:
            risk_label = "medium_fake_risk"
            action = "show_fake_warning_but_treat_as_normal"
        else:
            risk_label = "low_fake_risk"
            action = "treat_as_normal"

        # Remove duplicates from suspicious words list
        suspicious_words_list = list(set(suspicious_words_list))

        return FakeCallResult(
            fake_score=fake_score,
            risk_label=risk_label,
            action=action,
            text_features=text_features,
            behavior_features=behavior_features,
            suspicious_words=suspicious_words_list,
            word_contributions=word_contributions,
        )

    def analyze_call(
        self,
        transcript: str,
        p_fake_model: float,
        call_duration_sec: float = 0.0,
        repeat_call_count_last_hour: int = 0,
        depression_score: Optional[float] = None,
    ) -> FakeCallResult:
        """
        Main function you call from your system.

        Args:
            transcript: ASR text of the call (transcript from speech-to-text)
            p_fake_model: probability from your fake-call ML model (0–1)
            call_duration_sec: length of this call/segment (default: 0.0)
            repeat_call_count_last_hour: how many times this caller called in last hour (default: 0)
            depression_score: probability from your depression model (0–1, optional)

        Returns:
            FakeCallResult with fake_score, risk_label, suspicious_words, and word_contributions
        """
        text_features = self.extract_text_features(transcript)
        behavior_features = self.make_behavior_features(
            call_duration_sec=call_duration_sec,
            repeat_call_count_last_hour=repeat_call_count_last_hour,
        )
        return self.combine_scores(
            p_fake_model=p_fake_model,
            text_features=text_features,
            behavior_features=behavior_features,
            depression_score=depression_score,
        )

    def format_result_dict(self, result: FakeCallResult) -> Dict:
        """
        Convert FakeCallResult to a dictionary for easy JSON serialization or API responses.
        
        Args:
            result: FakeCallResult from analyze_call()
            
        Returns:
            Dictionary with all result information
        """
        return {
            "fake_score": result.fake_score,
            "fake_probability_percent": round(result.fake_score * 100, 2),
            "risk_label": result.risk_label,
            "action": result.action,
            "suspicious_words": result.suspicious_words,
            "word_contributions": result.word_contributions,
            "text_features": {
                "token_count": result.text_features.token_count,
                "nonsense_ratio": result.text_features.nonsense_ratio,
                "unique_word_ratio": result.text_features.unique_word_ratio,
                "joke_word_count": result.text_features.joke_word_count,
                "abuse_word_count": result.text_features.abuse_word_count,
                "joke_words_found": list(result.text_features.joke_words_found),
                "abuse_words_found": list(result.text_features.abuse_words_found),
                "nonsense_words": list(result.text_features.nonsense_words),
            },
            "behavior_features": {
                "call_duration_sec": result.behavior_features.call_duration_sec,
                "repeat_call_count_last_hour": result.behavior_features.repeat_call_count_last_hour,
            }
        }


# ---------- Example usage (you can delete this in production) ----------

if __name__ == "__main__":
    algo = FakeCallAlgorithm()

    # Example: your ML models already gave these scores
    p_fake_model = 0.6          # from your trained fake-call detector
    depression_score = 0.1      # from your depression model (optional)

    transcript = "hello this is a prank call lol lol lol just kidding"
    call_duration_sec = 8
    repeat_call_count_last_hour = 4

    result = algo.analyze_call(
        transcript=transcript,
        p_fake_model=p_fake_model,
        call_duration_sec=call_duration_sec,
        repeat_call_count_last_hour=repeat_call_count_last_hour,
        depression_score=depression_score,  # Optional parameter
    )

    # Print detailed results
    print("\n" + "="*60)
    print("FAKE CALL DETECTION ANALYSIS")
    print("="*60)
    print(f"Transcript: {transcript}")
    print(f"\nModel Output:")
    print(f"  Base Model Probability: {p_fake_model:.4f} ({p_fake_model*100:.2f}%)")
    print(f"\nFinal Analysis:")
    print(f"  Fake Score: {result.fake_score:.4f} ({result.fake_score*100:.2f}%)")
    print(f"  Risk Label: {result.risk_label}")
    print(f"  Recommended Action: {result.action}")
    
    print(f"\nSuspicious Words Found:")
    if result.suspicious_words:
        for word in result.suspicious_words:
            print(f"  - '{word}'")
    else:
        print("  (none)")
    
    print(f"\nWord Contributions:")
    for feature, contribution in result.word_contributions.items():
        print(f"  {feature}: {contribution:+.4f}")
    
    print(f"\nText Features:")
    print(f"  Total Tokens: {result.text_features.token_count}")
    print(f"  Nonsense Ratio: {result.text_features.nonsense_ratio:.4f}")
    print(f"  Unique Word Ratio: {result.text_features.unique_word_ratio:.4f}")
    print(f"  Joke Words: {result.text_features.joke_word_count}")
    print(f"  Abuse Words: {result.text_features.abuse_word_count}")
    
    print(f"\nBehavior Features:")
    print(f"  Call Duration: {result.behavior_features.call_duration_sec:.1f} seconds")
    print(f"  Repeat Calls (last hour): {result.behavior_features.repeat_call_count_last_hour}")
    print("="*60)
