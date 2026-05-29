"""Structural safety refusals. The harness is broker-free, network-free, key-free, and live-free BY CONSTRUCTION.
These functions exist to make any forbidden action raise loudly rather than proceed."""


class SafetyViolation(RuntimeError):
    pass


def connect_broker(*args, **kwargs):
    raise SafetyViolation("NO_BROKER: broker connection is structurally forbidden in the forward-paper harness.")


def place_live_order(*args, **kwargs):
    raise SafetyViolation("NO_LIVE_TRADING: live order placement is structurally forbidden; this is a simulated paper harness.")


def paper_trade_via_broker(*args, **kwargs):
    raise SafetyViolation("NO_PAPER_VIA_BROKER: brokerage paper accounts are forbidden; fills are simulated from LOCAL data only.")


def submit_to_strategy_lab(*args, **kwargs):
    raise SafetyViolation("NO_STRATEGY_LAB_PROMOTION: promotion is forbidden; s21 is DIAGNOSTIC_ONLY.")


def request_frc(*args, **kwargs):
    raise SafetyViolation("FRC_NEVER_GRANTED: this harness cannot request or grant FRC.")


def fetch_market_data(*args, **kwargs):
    raise SafetyViolation("NO_FETCH: this harness never fetches data or touches the network; supply LOCAL split_only CSVs.")


def assert_no_api_key_access(env_like=None):
    """Refuse if any secret/API-key-looking variable is present in a passed mapping. The harness never reads the process environment itself."""
    if env_like:
        for k in env_like:
            up = str(k).upper()
            if "API_KEY" in up or "TOKEN" in up or "SECRET" in up or up.endswith("_KEY"):
                raise SafetyViolation("NO_API_KEYS: the forward-paper harness must not access API keys or secrets (saw %r)." % k)
    return True


def assert_safe_environment(live_mode=False, broker=None):
    if live_mode:
        raise SafetyViolation("LIVE_MODE_DETECTED: refuse to run; paper harness is simulated-only.")
    if broker is not None:
        raise SafetyViolation("BROKER_DETECTED: refuse to run; broker-free only.")
    return True
