"""按纯文本规则判断一条路径要不要略过。只使用语言自带功能。"""

from hulue.match import should_skip
from hulue.parse import load_rules

__version__ = "0.3.1"

__all__ = ["load_rules", "should_skip", "__version__"]
