# Measured contract charts

Written by `python3 -m tcvm.cli charts`.

| Opcode | Gas |
| --- | --- |
| PUSH | 1 |
| ADD | 1 |
| SUB | 1 |
| EQ | 1 |
| GE | 1 |
| ASSERT | 1 |
| ARG | 1 |
| CALLVALUE | 1 |
| SLOAD | 1 |
| SSTORE | 5 |
| PAYOUT | 1 |
| SWAP | 1 |
| JUMPI | 1 |
| JUMP | 1 |
| STOP | 0 |

Deposit gas: 21. Withdraw gas: 30.
Unknown action completed 7 gas before the assert.
STOP charges nothing. SSTORE charges 5. The other completed opcodes charge 1.
