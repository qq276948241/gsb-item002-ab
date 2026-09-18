import unittest

from hulue import should_skip


class StarStaysInOneLayer(unittest.TestCase):
    def test_single_star_does_not_cross_slash(self):
        rules = "a*c.log\n"
        self.assertTrue(should_skip("abc.log", False, rules))
        self.assertFalse(should_skip("a/b/c.log", False, rules))

    def test_star_with_slash_stays_in_one_layer(self):
        rules = "src/*.log\n"
        self.assertTrue(should_skip("src/err.log", False, rules))
        self.assertFalse(should_skip("src/sub/err.log", False, rules))
        self.assertFalse(should_skip("other/src/err.log", False, rules))


class DoubleStarCrossesLayers(unittest.TestCase):
    def test_double_star_allows_zero_layers(self):
        rules = "手稿/**/附注\n"
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/甲/附注", False, rules))
        self.assertTrue(should_skip("手稿/甲/乙/附注", False, rules))
        self.assertFalse(should_skip("附注", False, rules))
        self.assertFalse(should_skip("别的/附注", False, rules))

    def test_double_star_at_start_matches_any_depth(self):
        rules = "**/附注\n"
        self.assertTrue(should_skip("附注", False, rules))
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/套层/附注", False, rules))


class DirectoriesAndFiles(unittest.TestCase):
    def test_trailing_slash_matches_directory_only(self):
        rules = "foo/\n"
        self.assertTrue(should_skip("foo", True, rules))
        self.assertFalse(should_skip("foo", False, rules))

    def test_directory_rule_covers_contents(self):
        rules = "foo/\n"
        self.assertTrue(should_skip("foo/bar.txt", False, rules))
        self.assertTrue(should_skip("foo/sub/bar.txt", False, rules))
        self.assertFalse(should_skip("bar/foo", False, rules))

    def test_plain_name_matches_file_and_directory(self):
        rules = "foo\n"
        self.assertTrue(should_skip("foo", False, rules))
        self.assertTrue(should_skip("foo", True, rules))


class Anchoring(unittest.TestCase):
    def test_leading_slash_anchors_to_root(self):
        rules = "/foo\n"
        self.assertTrue(should_skip("foo", False, rules))
        self.assertFalse(should_skip("a/foo", False, rules))

    def test_no_slash_matches_any_layer(self):
        rules = "附注\n"
        self.assertTrue(should_skip("附注", False, rules))
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/套层/附注", True, rules))


class NegationOrdering(unittest.TestCase):
    def test_later_plain_rule_reignores(self):
        rules = "*.log\n!keep.log\nkeep.log\n"
        self.assertFalse(should_skip("other.txt", False, rules))
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertTrue(should_skip("keep.log", False, rules))

    def test_later_negation_brings_back(self):
        rules = "foo\n!foo\n"
        self.assertFalse(should_skip("foo", False, rules))

    def test_early_negation_does_not_block_later_rule(self):
        rules = "!a.log\n*.log\n"
        self.assertTrue(should_skip("a.log", False, rules))

    def test_negation_recovers_contents_under_skipped_directory(self):
        rules = "foo\n!foo/bar\n"
        self.assertFalse(should_skip("foo/bar", False, rules))
        self.assertTrue(should_skip("foo/baz", False, rules))


class CommentsAndEscapes(unittest.TestCase):
    def test_blank_and_comment_lines_with_leading_spaces(self):
        rules = "   \n\t# 只是说明\n   # 也是说明\n*.log\n"
        self.assertTrue(should_skip("err.log", False, rules))

    def test_escaped_hash_is_literal(self):
        rules = r"\#readme" + "\n"
        self.assertTrue(should_skip("#readme", False, rules))

    def test_escaped_bang_is_literal_not_negation(self):
        rules = r"\!keep.log" + "\n"
        self.assertTrue(should_skip("!keep.log", False, rules))
        self.assertFalse(should_skip("keep.log", False, rules))


if __name__ == "__main__":
    unittest.main()
