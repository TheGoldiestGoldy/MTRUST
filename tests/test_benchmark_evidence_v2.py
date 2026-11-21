"""Negative and positive regression checks for Stage 1 phase/clock evidence."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import benchmark_tsc_v2 as v2


def timeline():
    names = list(v2.PHASES)
    return [
        {"phase": name, "java_monotonic_ns": i * 1_000_000_000,
         "received_monotonic_ns": i * 1_000_000_000 + 1_000_000}
        for i, name in enumerate(names)
    ]


def result_line(rails=64, calls=20, warmup_ns=2_000_000_000,
                clock_change=20_000, tick_values=None):
    durations = tick_values or ["0.125"] * calls
    return "|".join(map(str, [
        "RESULT", rails, calls, ",".join(durations), 5000000, 134217728, 0,
        0, 0, 25000, rails, 40, warmup_ns, 1000000000, 1720000000000,
        1720000000000 + clock_change,
    ]))


class PhaseTests(unittest.TestCase):
    def test_monotonic_complete_protocol(self):
        v2.validate_clock(timeline())

    def test_rejects_missing_phase(self):
        t = timeline()
        t.pop(3)
        with self.assertRaises(ValueError):
            v2.validate_clock(t)

    def test_rejects_reversed_phase_time(self):
        t = timeline()
        t[3]["java_monotonic_ns"] = t[2]["java_monotonic_ns"] - 1
        with self.assertRaises(ValueError):
            v2.validate_clock(t)

    def test_rejects_clock_domain_misalignment(self):
        t = timeline()
        t[3]["received_monotonic_ns"] += 900_000_000
        with self.assertRaises(ValueError):
            v2.validate_clock(t)

    def test_phase_boundary_and_save_not_ticking(self):
        t = timeline()
        samples = [
            {"monotonic_ns": 2_000_000_001, "rss_bytes": 10, "pss_bytes": 8},
            {"monotonic_ns": 2_500_000_000, "rss_bytes": 20, "pss_bytes": 15},
            {"monotonic_ns": 3_500_000_000, "rss_bytes": 999, "pss_bytes": 900},
            {"monotonic_ns": 5_500_000_000, "rss_bytes": 1000, "pss_bytes": 970},
        ]
        v2.classify_samples(samples, t)
        self.assertEqual([x["phase"] for x in samples], [
            "transition_excluded", "ticks", "save", "idle",
        ])
        memory = v2.summarize_memory(samples)
        self.assertEqual(memory["ticks"]["rss_bytes"], [20])
        self.assertEqual(memory["sampled_process_peak"]["rss_bytes"], 1000)

    def test_short_phase_never_invents_samples(self):
        t = timeline()
        samples = [{"monotonic_ns": 3_000_000_001, "rss_bytes": 300, "pss_bytes": 200}]
        v2.classify_samples(samples, t)
        self.assertEqual(v2.summarize_memory(samples)["save"]["count"], 0)


class ClockTests(unittest.TestCase):
    def test_deterministic_step(self):
        parsed = v2.safe_result_fields(result_line(), 64, 20, 2)
        self.assertEqual(parsed["internal_tick_step_ms"], 1000)
        self.assertEqual(parsed["virtual_clock_after_ms"] -
                         parsed["virtual_clock_before_ms"], 20000)

    def test_rejects_discontinuous_clock(self):
        with self.assertRaisesRegex(ValueError, "clock"):
            v2.safe_result_fields(result_line(clock_change=19_000), 64, 20, 2)

    def test_rejects_too_short_actual_warmup(self):
        with self.assertRaisesRegex(ValueError, "Warmup"):
            v2.safe_result_fields(result_line(warmup_ns=1_999_999_999), 64, 20, 2)

    def test_rejects_nonfinite_samples(self):
        vals = ["0.1"] * 19 + ["nan"]
        with self.assertRaisesRegex(ValueError, "tick"):
            v2.safe_result_fields(result_line(tick_values=vals), 64, 20, 2)

    def test_rejects_count_mismatch(self):
        with self.assertRaisesRegex(ValueError, "count"):
            v2.safe_result_fields(result_line(rails=64), 0, 20, 2)

    def test_rejects_incomplete_result(self):
        with self.assertRaisesRegex(ValueError, "Malformed"):
            v2.safe_result_fields("RESULT|1|2", 1, 20, 2)


class NativeMemoryTests(unittest.TestCase):
    def test_parses_nmt_summary_without_claiming_core_attribution(self):
        sample = """Native Memory Tracking:
Total: reserved=921600KB, committed=168960KB
- Java Heap (reserved=524288KB, committed=131072KB)
- Thread (reserved=20480KB, committed=2048KB)
"""
        parsed = v2.parse_nmt_summary(sample)
        self.assertEqual(parsed["committed_kb"], 168960)
        self.assertEqual(parsed["categories"]["Java Heap"]["committed_kb"], 131072)
        self.assertIn("whole JVM", parsed["scope"])

    def test_rejects_missing_nmt_totals(self):
        with self.assertRaises(ValueError):
            v2.parse_nmt_summary("NMT disabled")


class HistoricalEvidenceTests(unittest.TestCase):
    def test_immutable_historical_statistics_are_reproducible(self):
        original = json.loads((ROOT / "metrics/stage1-raw.json").read_text())
        expected = {
            "S0_empty": ("0.011685", "0.029911", "0.033664"),
            "T1_rail_topology_64": ("0.043479", "0.138011", "0.173964"),
            "T2_rail_topology_512": ("0.260449", "0.382223", "0.471665"),
        }
        for scenario, recorded in expected.items():
            calls = [v for run in original["runs"] if run["scenario"] == scenario
                     for v in run["sample_tsc_tick_ms"]]
            self.assertEqual(len(calls), 120)
            self.assertEqual(v2.quantiles(calls), recorded)
        # V1 memory samples lack phase/timestamp and cannot be reconstructed.
        self.assertNotIn("phase_events", original["runs"][0])
        self.assertNotIn("memory_samples", original["runs"][0])


if __name__ == "__main__":
    unittest.main()
