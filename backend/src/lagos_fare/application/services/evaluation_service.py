"""
Model evaluation module — MAE, RMSE, R², MAPE + dissertation charts.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sns.set_theme(style="whitegrid", context="paper")


class EvaluationService:
    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "model") -> dict:
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))
        mape = float(np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1, None))) * 100)

        metrics = {
            "model": model_name,
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "mape": round(mape, 2),
            "n_samples": len(y_true),
        }

        metrics_path = self._output_dir / "model_metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        pd.DataFrame([metrics]).to_csv(self._output_dir / "metrics_table.csv", index=False)
        pd.DataFrame([metrics]).to_excel(self._output_dir / "metrics_table.xlsx", index=False)

        self._actual_vs_predicted(y_true, y_pred)
        self._residual_plot(y_true, y_pred)
        self._write_summary(metrics)

        return metrics

    def _actual_vs_predicted(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.scatter(y_true, y_pred, alpha=0.4, edgecolors="k", linewidths=0.3)
        lim = max(y_true.max(), y_pred.max()) * 1.05
        ax.plot([0, lim], [0, lim], "r--", label="Perfect prediction")
        ax.set_xlabel("Actual Fare (₦)")
        ax.set_ylabel("Predicted Fare (₦)")
        ax.set_title("Figure 4.7: Actual vs Predicted Fare")
        ax.legend()
        fig.savefig(self._output_dir / "07_actual_vs_predicted.png", bbox_inches="tight")
        plt.close(fig)

    def _residual_plot(self, y_true: np.ndarray, y_pred: np.ndarray) -> None:
        residuals = y_true - y_pred
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(y_pred, residuals, alpha=0.4)
        ax.axhline(0, color="red", linestyle="--")
        ax.set_xlabel("Predicted Fare (₦)")
        ax.set_ylabel("Residual (₦)")
        ax.set_title("Figure 4.8: Residual Plot")
        fig.savefig(self._output_dir / "08_residual_plot.png", bbox_inches="tight")
        plt.close(fig)

    def _write_summary(self, metrics: dict) -> None:
        summary = f"""# Model Performance Summary

| Metric | Value |
|--------|-------|
| MAE | ₦{metrics['mae']:,.2f} |
| RMSE | ₦{metrics['rmse']:,.2f} |
| R² | {metrics['r2']:.4f} |
| MAPE | {metrics['mape']:.2f}% |
| Samples | {metrics['n_samples']} |

The model explains {metrics['r2']*100:.1f}% of fare variance with a mean absolute error of ₦{metrics['mae']:,.0f}.
"""
        (self._output_dir / "model_performance_summary.md").write_text(summary, encoding="utf-8")
