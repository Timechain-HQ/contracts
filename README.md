# Timecoin contracts

Testnet contracts for Timecoin. This is not a mainnet contract system.

The machine and the vault bytecode run inside [Timecoin](https://github.com/Timechain-HQ/Timecoin). The block rules are in the [book](https://github.com/Timechain-HQ/book).

## Account

A contract account stores:

- bytecode
- an ML-DSA-44 capability public key
- a TIME balance
- integer storage

Only a transaction signed by that capability key may change the account. The chain does not keep a personal account for the caller.

## Machine

The machine is a stack interpreter with a gas limit of 10,000. It has no external calls. Every node that runs the same code, arguments, call value, and storage reaches the same storage and the same payout.

Opcodes: `PUSH`, `ADD`, `SUB`, `EQ`, `GE`, `ASSERT`, `ARG`, `CALLVALUE`, `SLOAD`, `SSTORE`, `PAYOUT`, `SWAP`, `JUMPI`, `JUMP`, `STOP`.

`SSTORE` costs 5 gas. The other opcodes cost 1. A failed assert, a bad jump, a negative payout, or an empty gas tank reverts the whole transaction.

## Vault

The vault is the first contract.

- Argument 0 selects the action. `1` deposits. `2` withdraws. Anything else reverts.
- Argument 1 is the amount.
- Deposit requires the attached call value to equal argument 1. The amount is added to storage slot 0. The payout is 0.
- Withdrawal requires a call value of 0 and a stored balance at least as large as argument 1. Storage slot 0 decreases by that amount. The payout is argument 1.

The chain checks the same movement against the contract's TIME balance: deposits increase it, payouts decrease it, and it cannot go negative.

## Conservation

For a call, the spent notes, the new notes, the fee, the call value, and the payout satisfy:

```text
inputs = outputs + fee + callvalue - payout
```

A deployment may lock input value in the new contract after paying its outputs and fee. The capability key must sign that deployment.
