"""
plots.py - Гишүүн 3: график зурах функцууд
Багтсан функцууд:
    plot_hist  - histogram (дундаж, медианы шугамтай)
    plot_box   - бүлэг бүрийн тархалтыг boxplot-оор харьцуулах
    plot_corr  - тоон багануудын корреляцийн heatmap
    plot_bar   - бүлэглэсэн баганан график (жишээ нь жил x хүйс)
    plot_line  - шугаман график (жилийн өөрчлөлт)
Бүх функц: path өгвөл PNG болгон хадгална, show=False бол дэлгэцэнд гаргахгүй.
Шаардлага: pandas, matplotlib, seaborn
"""
import os
import warnings
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore

# seaborn + matplotlib 3.10 хослолын хор хөнөөлгүй анхааруулгыг далдлах
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)


def _finish(path=None, show=True):
    """Графикийг хадгалж (path өгсөн бол), дараа нь харуулж/хаана."""
    plt.tight_layout()
    if path:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print("хадгалсан:", path)
    if show:
        plt.show()
    plt.close()


def _labels(ax, title=None, xlabel=None, ylabel=None):
    """Гарчиг, тэнхлэгийн нэрийг нэг дор тохируулна."""
    if title:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)


def plot_hist(df, col, path=None, bins=30, title=None, xlabel=None,
              ylabel=None, color="steelblue", edgecolor="white", show=True):
    """Histogram, дундаж ба медианы шугамтай."""
    data = df[col].dropna()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(data, bins=bins, color=color, edgecolor=edgecolor)
    ax.axvline(data.mean(), color="orange", lw=3, label=f"дундаж = {data.mean():.2f}")
    ax.axvline(data.median(), color="red", lw=2, ls="--", label=f"медиан = {data.median():.2f}")
    _labels(ax, title or col, xlabel, ylabel)
    ax.legend()
    _finish(path, show)


def plot_box(df, x, y, path=None, title=None, xlabel=None, ylabel=None,
             palette=None, order=None, ylim=None, rotate=0, show=True):
    """Бүлэг бүрийн тархалтыг boxplot-оор харьцуулна.
    order  - бүлгүүдийн эрэмбэ (жишээ нь боловсролын түвшин)
    ylim   - (min, max): хэт том утга (outlier) графикийг дарахаас сэргийлнэ
    rotate - x тэмдэглэгээний эргэлт (урт нэртэй бүлэгт 30-45)"""
    fig, ax = plt.subplots(figsize=(8 if rotate else 7, 4.5))
    if palette is not None:
        # hue=x өгснөөр seaborn-ы палитр анхааруулгагүй ажиллана
        sns.boxplot(data=df, x=x, y=y, hue=x, palette=palette, order=order,
                    hue_order=order, legend=False, ax=ax)
    else:
        sns.boxplot(data=df, x=x, y=y, color="steelblue", order=order, ax=ax)
    if ylim:
        ax.set_ylim(*ylim)
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")
    _labels(ax, title or f"{y} ба {x}", xlabel, ylabel)
    _finish(path, show)


def plot_corr(df, path=None, title="Корреляц", show=True):
    """Тоон багануудын корреляцийн heatmap."""
    fig, ax = plt.subplots(figsize=(7, 5.5))
    corr = df.select_dtypes("number").corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    ax.set_title(title)
    _finish(path, show)


def plot_bar(df, x, y, hue=None, path=None, title=None, xlabel=None,
             ylabel=None, palette=None, order=None, rotate=0, ylim=None,
             annotate=True, show=True):
    """Бүлэглэсэн баганан график. hue өгвөл x бүр дээр хэд хэдэн багана гарна
    (жишээ нь x=жил, hue=хүйс). df нь аль хэдийн нэгтгэсэн (жишээ нь median) байх ёстой."""
    fig, ax = plt.subplots(figsize=(9 if rotate else 7, 4.5))
    sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette, order=order,
                errorbar=None, ax=ax, **({} if hue else {"color": "steelblue"}))
    if annotate:
        for c in ax.containers:
            ax.bar_label(c, fmt="%.1f" if df[y].abs().max() >= 10 else "%.2f", fontsize=8, padding=2)
    if ylim:
        ax.set_ylim(*ylim)
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")
    _labels(ax, title or y, xlabel, ylabel)
    _finish(path, show)


def plot_line(df, x, y, hue=None, path=None, title=None, xlabel=None,
              ylabel=None, palette=None, ylim=None, xticks=None, show=True):
    """Шугаман график (цэгтэй). Жил/насны бүлгээр өөрчлөлт харуулахад тохиромжтой.
    hue өгвөл бүлэг бүрт тусдаа шугам зурна."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, marker="o", ax=ax)
    if xticks is not None:
        ax.set_xticks(xticks)
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="y", alpha=0.3)
    _labels(ax, title or y, xlabel, ylabel)
    _finish(path, show)