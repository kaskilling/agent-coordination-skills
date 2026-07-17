from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "reproduce_confirmatory_v3_public.py"
SPEC = importlib.util.spec_from_file_location("confirmatory_v3_reproduction", SCRIPT)
assert SPEC and SPEC.loader
reproduction = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reproduction)


class ConfirmatoryV3PublicReproductionTests(unittest.TestCase):
    def test_nested_values_within_tolerance_match(self) -> None:
        reproduction._assert_equivalent(
            {"gate": True, "posterior": [0.5, 1.0]},
            {"gate": True, "posterior": [0.5 + 1e-13, 1.0]},
        )

    def test_numeric_difference_outside_tolerance_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, r"\$\.posterior\[0\]"):
            reproduction._assert_equivalent(
                {"posterior": [0.5]},
                {"posterior": [0.500001]},
            )

    def test_boolean_is_not_treated_as_numeric(self) -> None:
        with self.assertRaisesRegex(ValueError, r"\$\.gate"):
            reproduction._assert_equivalent({"gate": True}, {"gate": 1})


if __name__ == "__main__":
    unittest.main()
