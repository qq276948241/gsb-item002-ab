import unittest

from hulue import should_skip


class SimpleCases(unittest.TestCase):
    def test_exact_name(self):
        rules = "readme.txt\n"
        self.assertTrue(should_skip("readme.txt", False, rules))
        self.assertFalse(should_skip("other.txt", False, rules))

    def test_star_suffix_at_root(self):
        rules = "*.log\n"
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertFalse(should_skip("err.txt", False, rules))

    def test_blank_and_comment(self):
        rules = "\n# 这是说明\n*.log\n"
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertFalse(should_skip("notes.txt", False, rules))

    def test_negation_when_it_is_the_later_hit(self):
        rules = "*.log\n!keep.log\n"
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertFalse(should_skip("keep.log", False, rules))


if __name__ == "__main__":
    unittest.main()
