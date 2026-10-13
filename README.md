# Timecoin contracts

The Timecoin contract machine. The token is Timecoin. The ticker is TIC. The node that applies these calls is <https://github.com/9lordisgod/Timecoin>.

Organization node: <https://github.com/Timechain-HQ/Timecoin>

A contract account stores bytecode, an ML-DSA-44 capability key, a TIC balance, and integer storage. Only a transaction signed by that capability key can change the account. The machine has no external calls.

```mermaid
flowchart TD
    arg{Argument 0}
    deposit[Call value equals argument 1]
    credit[Slot 0 and the TIC balance increase]
    withdraw[Slot 0 covers argument 1 and call value is 0]
    debit[Slot 0 decreases and the payout is argument 1]
    fail[Any other argument reverts]
    arg -->|1| deposit --> credit
    arg -->|2| withdraw --> debit
    arg -->|other| fail
```

`SSTORE` costs 5 gas. `STOP` costs 0. Every other completed opcode costs 1. The limit is 10,000 gas.

```text
inputs = outputs + fee + callvalue - payout
```

```bash
python3 -m unittest tests.test_vm
python3 -m tcvm.cli charts
```

![Gas per opcode](docs/charts/opcode-gas.png)

![Vault deposit gas](docs/charts/gas-deposit.png)

![Vault withdraw gas](docs/charts/gas-withdraw.png)

![Deposit stack depth](docs/charts/stack-deposit.png)

![Withdraw stack depth](docs/charts/stack-withdraw.png)

![Slot 0 after a 100-unit deposit and a 40-unit withdraw](docs/charts/storage.png)

![Gas completed before an unknown action reverts](docs/charts/revert.png)

Measured tables are in [docs/charts/README.md](docs/charts/README.md). The block rules are in the [book](https://github.com/Timechain-HQ/book).
