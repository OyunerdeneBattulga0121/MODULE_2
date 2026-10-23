"""Гишүүн 4: plot_scatter"""
import matplotlib.pyplot as plt
import seaborn as sns

from .plots import _finish


def plot_scatter(df, x, y, hue=None, path=None):
    """Хоёр тоон баганын scatter, hue-ээр өнгөлнө."""
    plt.figure(figsize=(7, 4))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, alpha=0.5)
    plt.title(f"{y} ба {x}")
    _finish(path)
