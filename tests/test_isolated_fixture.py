"""Safety and non-claim tests for inert server fixture profile builder."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import create_isolated_fabric_fixture as fixture


class FixtureSafetyTests(unittest.TestCase):
    def test_variants_do_not_start_servers_or_accept_eula(self):
        files = fixture.profile_files(seed="")
        self.assertEqual(files["eula.txt"], "eula=false\n")
        self.assertIn("server-ip=127.0.0.1", files["server.properties"])
        self.assertIn("enable-rcon=false", files["server.properties"])
        self.assertIn("online-mode=true", files["server.properties"])
        self.assertIn("level-type=minecraft:flat", files["server.properties"])

    def test_target_counts_are_not_claimed_as_achieved(self):
        self.assertEqual(set(fixture.SCENARIO_PLAN), {"S0", "S1", "S2", "S3", "S4"})
        self.assertTrue(all(s["status"] == "NOT MEASURED" for s in fixture.SCENARIO_PLAN.values()))

    def test_rejects_existing_destination_and_outside_parent(self):
        with tempfile.TemporaryDirectory() as root:
            parent = Path(root) / "safe-scaffold"
            parent.mkdir()
            target = parent / "new-scene"
            self.assertEqual(fixture.validate_destination(target, parent), target)
            target.mkdir()
            with self.assertRaises(FileExistsError):
                fixture.validate_destination(target, parent)
            with self.assertRaises(ValueError):
                fixture.validate_destination(Path(root) / "not-allowed", parent)

    def test_rejects_nonrelease_reference_without_creating_profile(self):
        with tempfile.TemporaryDirectory() as root:
            original_parent = fixture.ISOLATION_PARENT
            fixture.ISOLATION_PARENT = Path(root)
            try:
                fake_jar = Path(root) / "other.jar"
                fake_jar.write_bytes(b"nonrelease")
                target = Path(root) / "untouched"
                with self.assertRaises(ValueError):
                    fixture.create(target, fake_jar, seed="")
                self.assertFalse(target.exists())
            finally:
                fixture.ISOLATION_PARENT = original_parent


if __name__ == "__main__":
    unittest.main()
