"""Gas and stack charts from the vault and from single instructions."""

from __future__ import annotations

from pathlib import Path

from tcvm.pngchart import bar_chart, line_chart
from tcvm.vm import VAULT, Step, VmError, run


def write_charts(directory: str | Path) -> dict[str, object]:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    costs = opcode_costs()
    deposit = trace(VAULT, {}, [1, 100], 100)
    withdraw = trace(VAULT, {0: 100}, [2, 40], 0)
    reverted = trace_revert(VAULT, {0: 10}, [9, 1], 0)
    names = [name for name, _cost in costs]
    bar_chart(
        path / "opcode-gas.png",
        "Gas charged by one completed instruction",
        "opcode",
        names,
        [("gas", [float(cost) for _name, cost in costs])],
    )
    _line(path / "gas-deposit.png", "Vault deposit gas", deposit, "gas", lambda step: step.gas_used)
    _line(path / "gas-withdraw.png", "Vault withdraw gas", withdraw, "gas", lambda step: step.gas_used)
    _line(path / "stack-deposit.png", "Vault deposit stack depth", deposit, "depth", lambda step: step.stack_depth)
    _line(path / "stack-withdraw.png", "Vault withdraw stack depth", withdraw, "depth", lambda step: step.stack_depth)
    bar_chart(
        path / "storage.png",
        "Vault slot 0 after deposit and withdraw",
        "call",
        ["deposit", "withdraw"],
        [("slot 0", [float(deposit_storage()), float(withdraw_storage())])],
    )
    bar_chart(
        path / "revert.png",
        "Gas of instructions that completed before a revert",
        "call",
        ["unknown"],
        [("gas", [float(reverted)])],
    )
    report = _report(costs, deposit, withdraw, reverted)
    (path / "README.md").write_text(report, encoding="utf-8")
    return {"costs": costs, "deposit_gas": deposit[-1].gas_used, "withdraw_gas": withdraw[-1].gas_used, "revert_gas": reverted}


def opcode_costs() -> list[tuple[str, int]]:
    samples = [
        ("PUSH", [("PUSH", 1)], 0),
        ("ADD", [("PUSH", 2), ("PUSH", 3), ("ADD",)], 2),
        ("SUB", [("PUSH", 5), ("PUSH", 2), ("SUB",)], 2),
        ("EQ", [("PUSH", 1), ("PUSH", 1), ("EQ",)], 2),
        ("GE", [("PUSH", 3), ("PUSH", 1), ("GE",)], 2),
        ("ASSERT", [("PUSH", 1), ("ASSERT",)], 1),
        ("ARG", [("ARG", 0)], 0),
        ("CALLVALUE", [("CALLVALUE",)], 0),
        ("SLOAD", [("PUSH", 0), ("SLOAD",)], 1),
        ("SSTORE", [("PUSH", 1), ("PUSH", 9), ("SSTORE",)], 2),
        ("PAYOUT", [("PUSH", 0), ("PAYOUT",)], 1),
        ("SWAP", [("PUSH", 1), ("PUSH", 2), ("SWAP",)], 2),
        ("JUMPI", [("PUSH", 0), ("JUMPI", 0)], 1),
        ("JUMP", [("JUMP", 1), ("STOP",)], 0),
        ("STOP", [("STOP",)], 0),
    ]
    measured: list[tuple[str, int]] = []
    for name, code, index in samples:
        steps: list[Step] = []
        kwargs = {}
        if name == "ARG":
            run(code, {}, [7], 0, steps=steps)
        elif name == "CALLVALUE":
            run(code, {}, [], 4, steps=steps)
        else:
            run(code, {}, [], 0, steps=steps)
        previous = 0 if index == 0 else steps[index - 1].gas_used
        measured.append((name, steps[index].gas_used - previous))
        del kwargs
    return measured


def trace(code, storage, args, callvalue) -> list[Step]:
    steps: list[Step] = []
    run(code, storage, args, callvalue, steps=steps)
    return steps


def trace_revert(code, storage, args, callvalue) -> int:
    steps: list[Step] = []
    try:
        run(code, storage, args, callvalue, steps=steps)
    except VmError:
        if not steps:
            return 0
        return steps[-1].gas_used
    raise RuntimeError("call should revert")


def deposit_storage() -> int:
    storage, payout, _gas = run(VAULT, {}, [1, 100], 100)
    if payout != 0:
        raise RuntimeError("deposit payout")
    return storage[0]


def withdraw_storage() -> int:
    storage, _payout, _gas = run(VAULT, {0: 100}, [2, 40], 0)
    return storage[0]


def _line(path: Path, title: str, steps: list[Step], ylabel: str, read) -> None:
    line_chart(
        path,
        title,
        "step",
        ylabel,
        [("vault", [(index, read(step)) for index, step in enumerate(steps)])],
    )


def _report(costs, deposit, withdraw, reverted: int) -> str:
    lines = [
        "# Measured contract charts",
        "",
        "Written by `python3 -m tcvm.cli charts`.",
        "",
        "| Opcode | Gas |",
        "| --- | --- |",
    ]
    for name, cost in costs:
        lines.append(f"| {name} | {cost} |")
    lines.extend(
        [
            "",
            f"Deposit gas: {deposit[-1].gas_used}. Withdraw gas: {withdraw[-1].gas_used}.",
            f"Unknown action completed {reverted} gas before the assert.",
            "STOP charges nothing. SSTORE charges 5. The other completed opcodes charge 1.",
            "",
        ]
    )
    return "\n".join(lines)
