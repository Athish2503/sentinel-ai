import numpy as np
import re
from typing import List, Dict, Any

class BehaviorExplainer:
    """
    Analyzes session feature metrics against baseline characteristics to identify 
    and explain the underlying cause of an anomaly (unexpected tool usage, unusual sequence, 
    abnormal execution counts, or unexpected arguments).
    """

    @staticmethod
    def explain(
        session_features: Dict[str, Any],
        baseline_features: List[Dict[str, Any]],
        vocabulary: List[str]
    ) -> List[str]:
        """
        Runs rules on session metrics against baseline runs to generate structured explanations.
        """
        reasons = []
        vocab_set = set(vocabulary)

        # 1. Unexpected tool usage
        unexpected_tools = [tool for tool in session_features["sequence"] if tool not in vocab_set]
        if unexpected_tools:
            unique_unexpected = sorted(list(set(unexpected_tools)))
            reasons.append(
                f"Unexpected tool usage: tool(s) {', '.join([repr(t) for t in unique_unexpected])} "
                f"are not part of the normal behavior baseline."
            )

        # 2. Abnormal sequence (bigram transitions and full sequence matching)
        baseline_sequences = [tuple(f["sequence"]) for f in baseline_features]
        baseline_bigrams = set()
        for seq in baseline_sequences:
            for i in range(len(seq) - 1):
                baseline_bigrams.add((seq[i], seq[i+1]))
                
        session_seq = tuple(session_features["sequence"])
        
        unusual_transitions = []
        for i in range(len(session_seq) - 1):
            transition = (session_seq[i], session_seq[i+1])
            if transition not in baseline_bigrams:
                unusual_transitions.append(f"'{transition[0]} -> {transition[1]}'")
                
        if unusual_transitions:
            reasons.append(
                f"Abnormal sequence: contains unusual tool transitions not observed in the baseline: {', '.join(unusual_transitions)}."
            )
        elif session_seq not in baseline_sequences and len(session_seq) > 0:
            reasons.append(
                f"Abnormal sequence: the tool call path {list(session_seq)} was never observed during baseline profiling."
            )

        # 3. Unusual execution count
        exec_counts = [f["execution_count"] for f in baseline_features]
        if exec_counts:
            max_count = max(exec_counts)
            mean_count = np.mean(exec_counts)
            std_count = np.std(exec_counts)
            
            session_count = session_features["execution_count"]
            if session_count > max_count or session_count > (mean_count + 2 * std_count):
                reasons.append(
                    f"Unusual execution count: session has {session_count} tool calls, "
                    f"exceeding the baseline maximum of {max_count} (average {mean_count:.1f})."
                )

        # 4. Abnormal parameters
        param_lens = [f["parameter_length"] for f in baseline_features]
        if param_lens:
            max_len = max(param_lens)
            mean_len = np.mean(param_lens)
            std_len = np.std(param_lens)
            
            session_param_len = session_features["parameter_length"]
            if session_param_len > max_len or session_param_len > (mean_len + 2 * std_len):
                reasons.append(
                    f"Abnormal parameters: argument character length of {session_param_len} "
                    f"exceeds the baseline normal maximum of {max_len} (average {mean_len:.1f})."
                )

        # Check for suspicious payload patterns in prompt text
        prompt = session_features.get("prompt", "")
        suspicious_pattern = re.compile(
            r"(union\s+select|select\s+.*\s+from|drop\s+table|delete\s+from|insert\s+into|"\
            r"chmod\s+|cat\s+/etc/passwd|sh\s+-c|/bin/sh|/bin/bash|<script|javascript:|\.\./\.\./)",
            re.IGNORECASE
        )
        if suspicious_pattern.search(prompt):
            reasons.append(
                "Abnormal parameters: detected suspicious patterns or potential security injection payloads in parameters/prompt."
            )

        return reasons
