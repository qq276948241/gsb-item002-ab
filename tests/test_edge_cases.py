import unittest

from hulue import should_skip


class StarCases(unittest.TestCase):
    def test_single_star_stays_in_one_level(self):
        rules = "手稿/*.log\n"
        self.assertTrue(should_skip("手稿/err.log", False, rules))
        self.assertFalse(should_skip("手稿/一层/err.log", False, rules))

    def test_bare_star_pattern_still_matches_any_level(self):
        rules = "*.log\n"
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertTrue(should_skip("手稿/err.log", False, rules))
        self.assertTrue(should_skip("手稿/一层/err.log", False, rules))

    def test_single_star_does_not_cross_slash(self):
        rules = "a*b\n"
        self.assertTrue(should_skip("axxb", False, rules))
        self.assertTrue(should_skip("dir/axxb", False, rules))
        self.assertFalse(should_skip("ax/xb", False, rules))


class GlobStarCases(unittest.TestCase):
    def test_double_star_in_the_middle_matches_zero_levels(self):
        rules = "手稿/**/附注\n"
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/一层/附注", False, rules))
        self.assertTrue(should_skip("手稿/一层/两层/附注", False, rules))
        self.assertFalse(should_skip("别处/附注", False, rules))

    def test_leading_double_star_matches_any_depth(self):
        rules = "**/附注\n"
        self.assertTrue(should_skip("附注", False, rules))
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/很深/的/一层/附注", False, rules))

    def test_double_star_alone_matches_everything(self):
        rules = "**\n"
        self.assertTrue(should_skip("随便什么", False, rules))
        self.assertTrue(should_skip("一/二/三", True, rules))


class DirectoryCases(unittest.TestCase):
    def test_trailing_slash_matches_directory_only(self):
        rules = "附注/\n"
        self.assertTrue(should_skip("附注", True, rules))
        self.assertFalse(should_skip("附注", False, rules))

    def test_directory_contents_are_skipped(self):
        rules = "附注/\n"
        self.assertTrue(should_skip("附注/里面.txt", False, rules))
        self.assertTrue(should_skip("手稿/附注/里面.txt", False, rules))
        self.assertTrue(should_skip("手稿/附注/再深/一层.txt", False, rules))

    def test_trailing_slash_combined_with_double_star(self):
        rules = "手稿/**/\n"
        self.assertTrue(should_skip("手稿/附注", True, rules))
        self.assertTrue(should_skip("手稿/附注/里面.txt", False, rules))
        self.assertFalse(should_skip("手稿", False, rules))

    def test_double_star_dir_rule_covers_deep_contents(self):
        rules = "手稿/**/附注/\n"
        self.assertTrue(should_skip("手稿/x/附注/里面.txt", False, rules))
        self.assertTrue(should_skip("手稿/附注/里面.txt", False, rules))
        self.assertFalse(should_skip("手稿/附注", False, rules))


class AnchorCases(unittest.TestCase):
    def test_leading_slash_anchors_to_start(self):
        rules = "/附注\n"
        self.assertTrue(should_skip("附注", False, rules))
        self.assertFalse(should_skip("手稿/附注", False, rules))

    def test_leading_slash_with_subpath(self):
        rules = "/手稿/附注\n"
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertFalse(should_skip("别处/手稿/附注", False, rules))


class BareNameCases(unittest.TestCase):
    def test_name_without_slash_matches_any_level(self):
        rules = "附注\n"
        self.assertTrue(should_skip("附注", False, rules))
        self.assertTrue(should_skip("手稿/附注", False, rules))
        self.assertTrue(should_skip("手稿/很深/附注", False, rules))


class CommentAndBlankCases(unittest.TestCase):
    def test_indented_comments_and_blanks_are_ignored(self):
        rules = "   \n\t# 这是说明\n   # 也是说明\n*.log\n"
        self.assertTrue(should_skip("err.log", False, rules))
        self.assertFalse(should_skip("notes.txt", False, rules))


class EscapeCases(unittest.TestCase):
    def test_escaped_hash_is_literal_name(self):
        rules = r"\#笔记" + "\n"
        self.assertTrue(should_skip("#笔记", False, rules))
        self.assertFalse(should_skip("笔记", False, rules))

    def test_escaped_bang_is_literal_name(self):
        rules = r"\!keep.log" + "\n"
        self.assertTrue(should_skip("!keep.log", False, rules))

    def test_escaped_star_is_literal(self):
        rules = r"a\*b" + "\n"
        self.assertTrue(should_skip("a*b", False, rules))
        self.assertFalse(should_skip("axb", False, rules))

    def test_escaped_backslash_is_literal(self):
        rules = r"a\\b" + "\n"
        self.assertTrue(should_skip("a\\b", False, rules))
        self.assertFalse(should_skip("axb", False, rules))


class OrderingCases(unittest.TestCase):
    def test_later_plain_rule_overrides_negation(self):
        rules = "*.log\n!keep.log\nkeep.log\n"
        self.assertTrue(should_skip("keep.log", False, rules))

    def test_last_real_match_wins(self):
        rules = "*.log\n!keep.log\n子目录/*.log\n"
        self.assertFalse(should_skip("keep.log", False, rules))
        self.assertTrue(should_skip("子目录/keep.log", False, rules))

    def test_negation_brings_back_only_when_latest(self):
        rules = "附注/\n!附注/要留.txt\n"
        self.assertTrue(should_skip("附注/别的.txt", False, rules))
        self.assertFalse(should_skip("附注/要留.txt", False, rules))


if __name__ == "__main__":
    unittest.main()
