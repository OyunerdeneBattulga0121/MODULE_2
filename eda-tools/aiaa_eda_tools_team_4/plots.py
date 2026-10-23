"""Гишүүн 3: plot_hist, plot_box, plot_corr"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def _finish(path=None):
    """path өгсөн бол графикийг файлд хадгалаад, дэлгэцэнд харуулна."""
    if path:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        print("хадгалсан:", path)
    plt.show()


def plot_hist(df, col, path=None):
    """Histogram, дундаж ба медианы шугамтай."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df[col], bins=30, edgecolor="white")
    ax.axvline(df[col].mean(), color="orange", lw=4, label=f"дундаж = {df[col].mean():.1f}")
    ax.axvline(df[col].median(), color="red", lw=2, ls="--", label=f"медиан = {df[col].median():.1f}")
    ax.set_title(col); ax.legend()
    _finish(path)


def plot_box(df, x, y, path=None):
    """Бүлэг бүрийн тархалтыг boxplot-оор харьцуулна."""
    plt.figure(figsize=(7, 4))
    sns.boxplot(data=df, x=x, y=y)
    plt.title(f"{y} ба {x}")
    _finish(path)


def plot_corr(df, path=None):
    """Тоон багануудын корреляцийн heatmap."""
    plt.figure(figsize=(8, 6))
    corr = df.select_dtypes("number").corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Корреляц")
    _finish(path)
