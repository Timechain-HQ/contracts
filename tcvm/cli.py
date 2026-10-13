"""Write the contract-machine charts."""

from __future__ import annotations

import sys
from pathlib import Path

from tcvm.measure import write_charts


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "charts":
        root = Path(__file__).resolve().parents[1]
        target = Path(sys.argv[2]) if len(sys.argv) == 3 else root / "docs" / "charts"
        measured = write_charts(target)
        print(f"wrote {target}")
        print(f"deposit {measured['deposit_gas']}  withdraw {measured['withdraw_gas']}")
        return
    print("Usage: python3 -m tcvm.cli charts [directory]", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
