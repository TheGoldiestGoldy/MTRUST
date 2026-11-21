"""Unit tests for Stage 1 benchmark safety/summary helpers."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_tsc.py"
spec = importlib.util.spec_from_file_location("benchmark_tsc", SCRIPT)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


class QuantilesTests(unittest.TestCase):
    def test_empty_returns_missing(self):
        self.assertEqual(bench.quantiles([]), ("", "", ""))

    def test_single_sample_has_no_fake_percentiles(self):
        self.assertEqual(bench.quantiles([42]), ("42.000000", "", ""))

    def test_nearest_rank_percentile(self):
        self.assertEqual(bench.quantiles([float(i) for i in range(1, 101)]),
                         ("50.500000", "95.000000", "99.000000"))

    def test_rejects_nonrelease_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / "fake.jar"
            fake.write_bytes(b"not the release")
            with self.assertRaises(ValueError):
                bench.verify_artifact(fake)

    def test_scenario_labels_not_misrepresented(self):
        self.assertEqual(bench.SCENARIOS, {
            "S0_empty": 0,
            "T1_rail_topology_64": 64,
            "T2_rail_topology_512": 512,
        })


if __name__ == "__main__":
    unittest.main()
