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
import os  # Фолдер үүсгэхэд ашиглана.
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore


def _finish(path=None, show=True):  # Зургийг хадгалах, харуулах тохиргоог авна.
    """Графикийг хадгалж (path өгсөн бол), дараа нь харуулж/хаана."""
    plt.tight_layout()  # Зураг доторх зайг автоматаар тааруулна.
    if path:  # Хадгалах зам өгөгдсөн эсэхийг шалгана.
        folder = os.path.dirname(path)  # Хадгалах замын фолдерыг авна.
        if folder:
            os.makedirs(folder, exist_ok=True)  # Байхгүй фолдерыг үүсгэнэ.
        plt.savefig(path, dpi=150, bbox_inches="tight")  # Зургийг PNG файлд хадгална.
        print("хадгалсан:", path)  # Хадгалсан замыг мэдээлнэ.
    if show:  # Дэлгэцэнд харуулах тохиргоог шалгана.
        plt.show()
    plt.close()  # Ашигласан зургийн нөөцийг чөлөөлнө.


def _labels(ax, title=None, xlabel=None, ylabel=None):
    """Гарчиг, тэнхлэгийн нэрийг нэг дор тохируулна."""
    if title:
        ax.set_title(title)  # Графикийн гарчгийг тохируулна.
    if xlabel is not None:  # X тэнхлэгийн нэр өгөгдсөн эсэхийг шалгана.
        ax.set_xlabel(xlabel)  # X тэнхлэгийн нэрийг тохируулна.
    if ylabel is not None:  # Y тэнхлэгийн нэр өгөгдсөн эсэхийг шалгана.
        ax.set_ylabel(ylabel)  # Y тэнхлэгийн нэрийг тохируулна.


def plot_hist(df, col, path=None, bins=30, title=None, xlabel=None,
              ylabel=None, color="steelblue", edgecolor="white", show=True):
    """Histogram, дундаж ба медианы шугамтай."""
    data = df[col].dropna()  # Сонгосон баганын хоосон утгыг хасна.
    fig, ax = plt.subplots(figsize=(7, 4))  # Зураг болон тэнхлэг үүсгэнэ.
    ax.hist(data, bins=bins, color=color, edgecolor=edgecolor)  # Утгуудын давтамжийг зурна.
    ax.axvline(data.mean(), color="orange", lw=3, label=f"дундаж = {data.mean():.2f}")  # Дундажийг босоо шугамаар тэмдэглэнэ.
    ax.axvline(data.median(), color="red", lw=2, ls="--", label=f"медиан = {data.median():.2f}")  # Медианыг тасархай шугамаар тэмдэглэнэ.
    _labels(ax, title or col, xlabel, ylabel)
    ax.legend()  # Тайлбарын тэмдэглэгээг харуулна.
    _finish(path, show)


def plot_box(df, x, y, path=None, title=None, xlabel=None, ylabel=None,  # Бүлэг болон хэмжих баганыг авна.
             palette=None, order=None, ylim=None, rotate=0, show=True):  # Өнгө, эрэмбэ, хязгаар зэргийг авна.
    """Бүлэг бүрийн тархалтыг boxplot-оор харьцуулна.
    order  - бүлгүүдийн эрэмбэ (жишээ нь боловсролын түвшин)
    ylim   - (min, max): хэт том утга (outlier) графикийг дарахаас сэргийлнэ
    rotate - x тэмдэглэгээний эргэлт (урт нэртэй бүлэгт 30-45)"""
    fig, ax = plt.subplots(figsize=(8 if rotate else 7, 4.5))  # Эргүүлсэн шошготой үед өргөн зураг үүсгэнэ.
    if palette is not None:  # Өнгөний палитр өгсөн эсэхийг шалгана.
        # hue=x өгснөөр seaborn-ы палитр анхааруулгагүй ажиллана
        sns.boxplot(data=df, x=x, y=y, hue=x, palette=palette, order=order,
                    hue_order=order, legend=False, ax=ax)  # Өгсөн өнгө, эрэмбээр boxplot зурна.
    else:  # Палитр өгөөгүй үед нэг өнгө хэрэглэнэ.
        sns.boxplot(data=df, x=x, y=y, color="steelblue", order=order, ax=ax)  # Нэг өнгийн boxplot зурна.
    if ylim:  # Y тэнхлэгийн хязгаар өгөгдсөн эсэхийг шалгана.
        ax.set_ylim(*ylim)  # Y тэнхлэгийн доод, дээд хязгаарыг тохируулна.
    if rotate:  # X шошгыг эргүүлэх шаардлагатай эсэхийг шалгана.
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")  # X тэнхлэгийн шошгыг эргүүлнэ.
    _labels(ax, title or f"{y} ба {x}", xlabel, ylabel)
    _finish(path, show)


def plot_corr(df, path=None, title="Корреляц", show=True): 
    """Тоон багануудын корреляцийн heatmap."""
    fig, ax = plt.subplots(figsize=(7, 5.5))  # Зураг болон тэнхлэг үүсгэнэ.
    corr = df.select_dtypes("number").corr()  # Тоон багануудын корреляцыг бодно.
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)  # Корреляцыг өнгөөр дүрсэлж утгыг бичнэ.
    ax.set_title(title)  # Графикийн гарчгийг тохируулна.
    _finish(path, show)


def plot_bar(df, x, y, hue=None, path=None, title=None, xlabel=None, 
             ylabel=None, palette=None, order=None, rotate=0, ylim=None,
             annotate=True, show=True):  # Утга бичих болон харуулах сонголт.
    """Бүлэглэсэн баганан график. hue өгвөл x бүр дээр хэд хэдэн багана гарна
    (жишээ нь x=жил, hue=хүйс). df нь аль хэдийн нэгтгэсэн (жишээ нь median) байх ёстой."""
    fig, ax = plt.subplots(figsize=(9 if rotate else 7, 4.5))  # Шошго эргэсэн эсэхээс зурагны өргөнийг сонгоно.
    sns.barplot(data=df, x=x, y=y, hue=hue, palette=palette, order=order,
                errorbar=None, ax=ax, **({} if hue else {"color": "steelblue"}))  # Нэгтгэсэн өгөгдлөөр баганан график зурна.
    if annotate:  # Баганан дээр тоон утга бичих эсэхийг шалгана.
        for c in ax.containers:  # Бүлэг бүрийн багануудыг давтана.
            ax.bar_label(c, fmt="%.1f" if df[y].abs().max() >= 10 else "%.2f", fontsize=8, padding=2)  # Баганан дээр утгыг бичнэ.
    if ylim:  # Y тэнхлэгийн хязгаар өгөгдсөн эсэхийг шалгана.
        ax.set_ylim(*ylim)  # Y тэнхлэгийн доод, дээд хязгаарыг тохируулна.
    if rotate:  # X шошгыг эргүүлэх шаардлагатай эсэхийг шалгана.
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right")  # X тэнхлэгийн шошгыг эргүүлнэ.
    _labels(ax, title or y, xlabel, ylabel)
    _finish(path, show)


def plot_line(df, x, y, hue=None, path=None, title=None, xlabel=None,  # Шугаман графикийн өгөгдөл, бүлгийг авна.
              ylabel=None, palette=None, ylim=None, xticks=None, show=True):  # Өнгө, тэнхлэг болон харуулах тохиргоог авна.
    """Шугаман график (цэгтэй). Жил/насны бүлгээр өөрчлөлт харуулахад тохиромжтой.
    hue өгвөл бүлэг бүрт тусдаа шугам зурна."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5))  # Зураг болон тэнхлэг үүсгэнэ.
    sns.lineplot(data=df, x=x, y=y, hue=hue, palette=palette, marker="o", ax=ax)  # Өгөгдлөөр цэгтэй шугам зурна.
    if xticks is not None:  # X тэнхлэгийн тэмдэглэгээ өгсөн эсэхийг шалгана.
        ax.set_xticks(xticks)  # X тэнхлэгийн тэмдэглэгээг өгсөн утгаар тохируулна.
    if ylim:  # Y тэнхлэгийн хязгаар өгөгдсөн эсэхийг шалгана.
        ax.set_ylim(*ylim)  # Y тэнхлэгийн доод, дээд хязгаарыг тохируулна.
    ax.grid(axis="y", alpha=0.3)  # Y тэнхлэгийн торыг бүдэг харуулна.
    _labels(ax, title or y, xlabel, ylabel)  
    _finish(path, show)