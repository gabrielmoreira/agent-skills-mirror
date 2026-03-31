import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def setup_chinese_font():
    """Configure matplotlib to render Chinese characters correctly.

    Tries a priority-ordered list of CJK fonts commonly available on
    macOS, Linux, and Windows.  Falls back to whatever the system has.
    """
    candidates = [
        # macOS
        "Heiti TC",
        "Hiragino Sans GB",
        "PingFang SC",
        "PingFang HK",
        "STHeiti",
        "Songti SC",
        "Arial Unicode MS",
        # Linux
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "WenQuanYi Micro Hei",
        "WenQuanYi Zen Hei",
        "Droid Sans Fallback",
        # Windows
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
    ]

    available = {f.name for f in fm.fontManager.ttflist}

    for font_name in candidates:
        if font_name in available:
            plt.rcParams["font.sans-serif"] = [font_name, "sans-serif"]
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["axes.unicode_minus"] = False
            return

    # Last resort: let matplotlib pick, but still fix minus sign
    plt.rcParams["axes.unicode_minus"] = False
