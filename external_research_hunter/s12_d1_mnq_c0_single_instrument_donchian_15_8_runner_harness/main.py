"""S12-D1 runner_main.py-companion: main entrypoint placeholder.

This module is a placeholder for future-phase orchestration. P3 BUILD
authors it; P3 BUILD does NOT invoke it. Future phases (P4 SMOKE / P6
IS / P10 OOS / P10.5 cost-stress) will dispatch through this entrypoint
only after their own explicit operator authorizations.

The module exists so that the package import surface is complete; if
this file is invoked directly at BUILD time it raises NotImplementedError
to prevent any accidental execution path.

No fetch. No Databento. No DATABENTO_API_KEY. No network IO. No
brokerage. No order submission.
"""
from __future__ import annotations


def main(*_, **__) -> None:
    """Placeholder; not invoked at BUILD.

    Future-phase orchestration will dispatch through this function after
    its own explicit operator authorization. P3 BUILD does NOT call this.
    """
    raise NotImplementedError(
        "s12-d1 main is a placeholder. Each subsequent phase (P4/P6/P10/P10.5) "
        "requires a separate fresh operator authorization block; this main "
        "is never invoked at P3 BUILD."
    )


if __name__ == "__main__":  # pragma: no cover
    # Direct invocation must fail loudly; BUILD never runs this.
    raise NotImplementedError(
        "Direct invocation of s12-d1 main is blocked. A fresh operator "
        "authorization is required for any phase invocation."
    )
