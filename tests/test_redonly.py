import redonly.redonly as ro
import tempfile
import shutil


class TestRedOnly():
    def setup_method(self, method):
        print("Creating a temp folder...")
        self.temp_folder = tempfile.mkdtemp()
        print(f"Folder {self.temp_folder} created!")

    def teardown_method(self, method):
        print(f"Removing {self.temp_folder}...")
        shutil.rmtree(self.temp_folder)
        print(f"Folder {self.temp_folder} removed!")
    
    def test_two_subs(self):
        redonly = ro.RedOnly(self.temp_folder, ["france", "amitheasshole"])
        assert redonly.generate(), "Failed to generate RedOnly!"
    
    def test_wrong_sub(self):
        redonly = ro.RedOnly(self.temp_folder, ["cesousnexistepasmongars"])
        assert not redonly.generate(), "Generation should not be successful for a non existent subreddit"
