"""Run: python3 -m unittest discover tests. Builds a tiny fake plugin tree; needs no Spriggit or real plugins."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = "Tamrielic Distribution.esp"
RULES = {"t": {"expected_substitutions": 1, "import_from_td": [], "new_outfits": [], "vanilla_override": {},
               "master_replace": {"remove": TD, "insert": ["ccbgssse041-netchleather.esl"]},
               "substitutions": {f"00087D:{TD}": {"cc_from": "netch"}}}}


def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


class ApplyPatch(unittest.TestCase):
    def run_mode(self, mode):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        os.makedirs(f"{root}/tools")
        shutil.copy(f"{HERE}/tools/apply_patch.py", f"{root}/tools")
        put(f"{root}/patch/rules.json", json.dumps(RULES))
        put(f"{root}/orig/RecordData.yaml", f"MasterReferences:\n  - Master: Skyrim.esm\n    FileSize: 0\n  - Master: {TD}\n    FileSize: 0\n")
        put(f"{root}/orig/Outfits/o - 000800_x.yaml", f"Items:\n- 00087D:{TD}\n")
        name = f"i - 00087D_{TD}.yaml"
        put(f"{root}/td/Armors/{name}", "Items:\n- 013922:Skyrim.esm\n")
        put(f"{root}/modules/netch/Armors/{name}", "Items:\n- 000801:ccbgssse041-netchleather.esl\n")
        r = subprocess.run([sys.executable, "-I", f"{root}/tools/apply_patch.py", "t", mode, f"{root}/orig", f"{root}/td",
                            f"{root}/modules", f"{root}/out"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return (open(f"{root}/out/Outfits/o - 000800_x.yaml").read(), open(f"{root}/out/RecordData.yaml").read())

    def test_creation_club_uses_module_item_and_master(self):
        item, masters = self.run_mode("creation-club")
        self.assertIn("000801:ccbgssse041-netchleather.esl", item)
        self.assertIn("ccbgssse041-netchleather.esl", masters)
        self.assertNotIn(TD, masters)

    def test_vanilla_uses_core_default_and_no_new_master(self):
        item, masters = self.run_mode("vanilla")
        self.assertIn("013922:Skyrim.esm", item)
        self.assertNotIn("ccbgs", masters)
        self.assertNotIn(TD, masters)


if __name__ == "__main__":
    unittest.main()
