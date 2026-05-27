"""Commander Research Autopilot v2.

Research-lifecycle control tower for the trading-research workflow.
NOT live trading. NOT paper trading. NOT strategy optimization.

Modules:
    state            -- CandidateState dataclass
    storage          -- file-based persistence
    git_sentinel     -- read-only git inspection
    phase_classifier -- classify commits by phase
    seal_verifier    -- recompute LESSON_HUNTER_004 canonical seal
    anchor_verifier  -- extract + verify parent_references
    gate_evaluator   -- extract K9 / DR / perf metrics from sealed JSON
    l1_checker       -- detect REC1_T1 carry status; recommend supplement
    decision_engine  -- generate pending decisions
    memo_writer      -- draft sealed memo bodies (no commits)
    safe_executor    -- approval-level-gated action runner

Hard guards (enforced by safe_executor + checked by every module):
    - never stage/modify brain_memory/projects/trading_bot/lessons.md
    - never touch live/paper trading or broker code
    - never relax K9 / DR thresholds
    - never claim profitability / live-readiness / OOS-confirmed
    - never modify already-sealed artifacts
    - never fetch Databento without explicit LEVEL_3 approval
    - never run P6 / P6.5 / P10 without explicit LEVEL_3 approval
"""

__version__ = "2.0.0"
