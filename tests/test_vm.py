"""Vault balances and the measured gas schedule."""

from __future__ import annotations

import unittest

from tcvm.measure import opcode_costs
from tcvm.vm import VAULT, VmError, run


class MachineTests(unittest.TestCase):
    def test_vault_moves_slot_zero(self) -> None:
        storage, payout, _gas = run(VAULT, {}, [1, 100], 100)
        self.assertEqual((storage[0], payout), (100, 0))
        storage, payout, _gas = run(VAULT, storage, [2, 40], 0)
        self.assertEqual((storage[0], payout), (60, 40))

    def test_unknown_action_and_gas_limit(self) -> None:
        with self.assertRaises(VmError):
            run(VAULT, {0: 10}, [9, 1], 0)
        with self.assertRaises(VmError):
            run(VAULT, {}, [1, 1], 1, gas_limit=3)

    def test_sstore_costs_five_and_stop_costs_nothing(self) -> None:
        costs = dict(opcode_costs())
        self.assertEqual(costs["SSTORE"], 5)
        self.assertEqual(costs["STOP"], 0)
        self.assertEqual(costs["PUSH"], 1)
        self.assertEqual(costs["ADD"], 1)
