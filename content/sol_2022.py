"""2022 年参考解与测试数据生成。"""
from __future__ import annotations

CUSTOMERS = {
    1: "断桥残雪, 领悟, 暗香, 隐形的翅膀, 再见, 白桦林, 流年, 一眼万年, 那些花儿, 雨一直下, 小城大事, 一剪梅",
    2: "暗香, 水手, 朋友, 流年, 再回首, 老鼠爱大米, 曾经的你, 一剪梅, 你的样子",
    3: "再回首, 黄昏",
    4: "梦醒时分, 隐形的翅膀, 朋友, 棉花糖, 难念的经, 小城大事, 一剪梅",
    5: "领悟, 父亲, 流年, 飘雪, 雨一直下, 童年, 遇见, 黄昏",
    6: "隐形的翅膀, 父亲, 大海, 一眼万年, 那些花儿, 飘雪, 同桌的你, 棉花糖, 曾经的你, 一剪梅, 慢慢",
    7: "遇见",
    8: "父亲, 飘雪, 黄昏, 曲终人散, 老鼠爱大米, 一剪梅",
    9: "领悟, 大海, 白桦林, 一剪梅, 同桌的你, 棉花糖, 难念的经, 曲终人散, 再回首, 黄昏, 你的样子",
    10: "再见, 水手, 朋友, 流年, 飘雪, 同桌的你, 雨一直下, 我是女生, 曲终人散, 再回首, 一剪梅, 你的样子",
}
LISTS = {k: [x.strip() for x in v.split(",")] for k, v in CUSTOMERS.items()}


def t1(data: str) -> str:
    s = data.strip()
    stops = {"TAG", "TAA", "TGA"}
    ok = len(s) >= 6 and len(s) % 3 == 0 and s[:3] == "ATG" and s[-3:] in stops
    if ok:
        for i in range(3, len(s) - 3, 3):
            if s[i:i + 3] in stops:
                ok = False
                break
    return ("是一种潜在的基因" if ok else "不是一种潜在的基因") + "\n"


def t2(data: str) -> str:
    user = set(data.split())
    best_id, best_hit = 0, -1
    for cid in range(1, 11):
        hit = len(user & set(LISTS[cid]))
        if hit > best_hit:
            best_hit, best_id = hit, cid
    rec = [s for s in LISTS[best_id] if s not in user] if best_hit > 0 else []
    prefix = "与您爱好相同的客户还点过这些歌曲："
    return prefix + (",".join(rec) if rec else "") + "\n"


def gen_t1(rng):
    return ["ATGCGCCTGCGTCTGTACTAG\n", "ATGTAG\n", "ATGAAATAG\n",
            "ATGAAATAA\n", "ATGTGA\n", "ATGCCCTAG\n", "ATGCCT\n",
            "CCCATGTAG\n", "ATGAAATTTCCCGGGTTTAG\n"]


def gen_t2(rng):
    return ["再见 遇见 童年\n", "再见\n", "一剪梅\n", "断桥残雪\n",
            "不存在的歌\n", "领悟 流年 雨一直下\n", "父亲 飘雪 黄昏\n"]


CASES = {
    "2022-t1": {
        "solve": t1,
        "samples": [("ATGCGCCTGCGTCTGTACTAG\n", "是一种潜在的基因"),
                    ("ATGCCCTAA\n", "是一种潜在的基因")],
        "tests": gen_t1,
    },
    "2022-t2": {
        "solve": t2,
        "samples": [("再见 遇见 童年\n", "与您爱好相同的客户还点过这些歌曲：领悟,父亲,流年,飘雪,雨一直下,黄昏")],
        "tests": gen_t2,
    },
}
