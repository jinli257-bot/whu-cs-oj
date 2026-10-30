"""2020 年参考解与测试数据生成。"""
from __future__ import annotations

import re

from .common import sieve


def t1(data: str) -> str:
    m = re.search(r"\d+", data)
    return (str(int(m.group())) if m else "0") + "\n"


def gen_t1(rng):
    return ["Ab123xyz874[429]2\n", "...007bond\n", "abc\n", "a1b2c3\n",
            "0000\n", "x99\n", "  42  \n"]


CASES = {
    "2020-t1": {
        "solve": t1,
        "samples": [("Ab123xyz874[429]2\n", "123"), ("...007bond\n", "7")],
        "tests": gen_t1,
    },
}
