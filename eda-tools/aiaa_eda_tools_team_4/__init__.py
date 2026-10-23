"""Гишүүн 4: сангийн нүүр. Бүх функцийг нэг дор гаргана."""
from .cleaning import missing_report, iqr_outliers
from .stats import basic_stats, group_rate
from .plots import plot_hist, plot_box, plot_corr
from .extra import plot_scatter
