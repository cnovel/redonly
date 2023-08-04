import redonly.redonly as ro
import tempfile
import shutil
import os


class TestRedOnly():
    def setup_method(self, method):
        print("Creating a temp folder...")
        self.temp_folder = tempfile.mkdtemp()
        print(f"Folder {self.temp_folder} created!")

    def teardown_method(self, method):
        print(f"Removing {self.temp_folder}...")
        shutil.rmtree(self.temp_folder)
        print(f"Folder {self.temp_folder} removed!")
    
    def test_two_french_subs(self):
        opts = ro.Options(ro.Language.fr, ro.Style.dark, False)
        redonly = ro.RedOnly(self.temp_folder, ["france", "Lyon"], opts)
        assert redonly.generate(), "Failed to generate RedOnly in French!"
    
    def test_two_minimal_subs(self):
        opts = ro.Options(style=ro.Style.minimal, target_old=True)
        redonly = ro.RedOnly(self.temp_folder, ["cpp", "Python"], opts)
        assert redonly.generate(), "Failed to generate RedOnly with minimal style!"

    def test_two_en_subs(self):
        redonly = ro.RedOnly(self.temp_folder, ["CasualUK", "news"])
        assert redonly.generate(), "Failed to generate RedOnly in English!"

    def test_wrong_sub(self):
        redonly = ro.RedOnly(self.temp_folder, ["cesousnexistepasmongars"])
        assert not redonly.generate(), "Generation should not be successful for a non existent subreddit"

    def test_locales(self):
        # en acts as the reference
        path_to_locale = f"{os.path.dirname(os.path.realpath(__file__))}/../src/redonly/data/locale"
        keys = set()
        with open(os.path.abspath(os.path.join(path_to_locale, "en.txt")), 'r') as locale:
            data = [line.strip().split(":", 1) for line in locale.readlines()]
            for d in data:
                keys.add(d[0])

        for lang in ro.Language:
            print(f"Checking {lang} locale")
            with open(os.path.join(path_to_locale, f"{lang}.txt"), 'r') as locale:
                data = [line.strip().split(":", 1) for line in locale.readlines()]
                assert len(data) == len(keys), f"Invalid number of keys for {lang}"
                for d in data:
                    assert len(d) == 2, f"Invalid data length for {lang}"
                    assert d[0] in keys, f"Invalid key for {lang}: {d[0]}"
                    assert len(d[1]) > 0, f"Empty localization string for {lang}: {d[0]}"
