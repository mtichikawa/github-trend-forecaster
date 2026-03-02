"""
src/models/prophet_model.py — Prophet hyperparameter configuration and tuning.

This module defines ProphetModelConfig, a dataclass that centralises all
tunable Prophet parameters in one place, and fit_with_config(), which applies
a config to train a RepoForecaster instance from prophet_forecast.py.

Why this exists:
    prophet_forecast.py wires Prophet with fixed defaults (weekly + yearly
    seasonality, no changepoint tuning). ProphetModelConfig lets you vary
    those parameters systematically — useful for grid search, backtesting
    different regimes, or quickly adjusting sensitivity for repos with
    irregular growth patterns (viral events, deprecations, renames).

Typical usage:
    >>> from src.models.prophet_model import ProphetModelConfig, fit_with_config
    >>> from src.models.prophet_forecast import RepoForecaster
    >>>
    >>> config = ProphetModelConfig(changepoint_prior_scale=0.05, n_forecast_days=90)
    >>> forecaster = RepoForecaster()
    >>> data = forecaster.load_data("tensorflow/tensorflow")
    >>> df = forecaster.prepare_data(data)
    >>> fit_with_config(forecaster, df, config)
    >>> forecast = forecaster.predict(periods=config.n_forecast_days)
"""

from dataclasses import dataclass, field
from typing import List, Optional

from prophet import Prophet


# ── Hyperparameter config ──────────────────────────────────────────────────────

@dataclass
class ProphetModelConfig:
    """
    All tunable parameters for a Prophet forecast model in one place.

    Attributes:
        changepoint_prior_scale:
            Flexibility of the trend at detected changepoints. Larger values
            allow the trend to change more sharply — useful for repos with
            sudden growth events (viral posts, framework adoption). Lower values
            produce smoother, more conservative trends.
            Typical range: 0.001 – 0.5. Default: 0.05.

        seasonality_prior_scale:
            Flexibility of seasonality components. Higher values allow
            seasonality to fit tighter to observed patterns; lower values
            treat seasonality as a weaker signal.
            Default: 10.0.

        seasonality_mode:
            'additive' — seasonality is a fixed offset from the trend.
            'multiplicative' — seasonality scales with trend magnitude.
            Use 'multiplicative' when percentage swings stay constant as
            the repo grows (common for popular repos).
            Default: 'additive'.

        weekly_seasonality:
            Whether to model day-of-week effects. Repos often see lower
            activity on weekends. Default: True.

        yearly_seasonality:
            Whether to model annual cycles. Useful for repos tied to
            conference seasons or academic calendars. Default: True.

        daily_seasonality:
            Whether to model hour-of-day effects. Rarely useful for
            daily-resolution star data. Default: False.

        n_changepoints:
            Maximum number of potential changepoints to consider.
            Default: 25 (Prophet default).

        interval_width:
            Width of the uncertainty interval in the forecast output.
            0.80 = 80% credible interval. Default: 0.80.

        n_forecast_days:
            Number of days into the future to forecast. Default: 90.

        extra_regressors:
            List of additional regressor column names in the training
            DataFrame (beyond 'ds' and 'y'). Each must be present in
            the DataFrame passed to fit_with_config(). Default: empty.
    """

    changepoint_prior_scale: float = 0.05
    seasonality_prior_scale: float = 10.0
    seasonality_mode:        str   = "additive"
    weekly_seasonality:      bool  = True
    yearly_seasonality:      bool  = True
    daily_seasonality:       bool  = False
    n_changepoints:          int   = 25
    interval_width:          float = 0.80
    n_forecast_days:         int   = 90
    extra_regressors:        List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.seasonality_mode not in ("additive", "multiplicative"):
            raise ValueError(
                f"seasonality_mode must be 'additive' or 'multiplicative', "
                f"got '{self.seasonality_mode}'"
            )
        if not 0 < self.interval_width < 1:
            raise ValueError(
                f"interval_width must be between 0 and 1, got {self.interval_width}"
            )
        if self.changepoint_prior_scale <= 0:
            raise ValueError("changepoint_prior_scale must be positive")

    def to_prophet_kwargs(self) -> dict:
        """
        Convert this config to keyword arguments suitable for Prophet().

        Returns:
            Dict of kwargs that can be passed directly to Prophet(**kwargs).
        """
        return {
            "changepoint_prior_scale": self.changepoint_prior_scale,
            "seasonality_prior_scale": self.seasonality_prior_scale,
            "seasonality_mode":        self.seasonality_mode,
            "weekly_seasonality":      self.weekly_seasonality,
            "yearly_seasonality":      self.yearly_seasonality,
            "daily_seasonality":       self.daily_seasonality,
            "n_changepoints":          self.n_changepoints,
            "interval_width":          self.interval_width,
        }

    def __repr__(self) -> str:
        return (
            f"ProphetModelConfig("
            f"changepoint_prior_scale={self.changepoint_prior_scale}, "
            f"seasonality_mode='{self.seasonality_mode}', "
            f"n_forecast_days={self.n_forecast_days})"
        )


# ── Fitting helper ─────────────────────────────────────────────────────────────

def fit_with_config(forecaster, df, config: ProphetModelConfig) -> None:
    """
    Train a RepoForecaster using the given ProphetModelConfig.

    This replaces RepoForecaster.train() when you want non-default
    hyperparameters. It builds a Prophet model from the config, fits it to
    df, and stores the result on the forecaster so that forecaster.predict()
    and forecaster.evaluate() work normally afterwards.

    Args:
        forecaster: A RepoForecaster instance (from prophet_forecast.py).
                    Its .model attribute will be replaced with the new model.
        df:         DataFrame with columns 'ds' (datetime) and 'y' (values),
                    and optionally any extra regressor columns listed in
                    config.extra_regressors.
        config:     ProphetModelConfig controlling all hyperparameters.

    Example:
        >>> config = ProphetModelConfig(changepoint_prior_scale=0.1,
        ...                             seasonality_mode='multiplicative')
        >>> fit_with_config(forecaster, df, config)
        >>> forecast = forecaster.predict(periods=config.n_forecast_days)
    """
    import logging
    log = logging.getLogger(__name__)

    model = Prophet(**config.to_prophet_kwargs())

    # Register any extra regressors before fitting
    for regressor in config.extra_regressors:
        if regressor not in df.columns:
            raise ValueError(
                f"Extra regressor '{regressor}' listed in config but not found "
                f"in DataFrame columns: {list(df.columns)}"
            )
        model.add_regressor(regressor)
        log.info(f"Added extra regressor: {regressor}")

    log.info(f"Training Prophet model with config: {config}")
    model.fit(df)
    forecaster.model = model
    log.info("Model training complete.")


# ── Preset configs ─────────────────────────────────────────────────────────────

CONFIGS = {
    "default": ProphetModelConfig(),

    "conservative": ProphetModelConfig(
        changepoint_prior_scale=0.01,
        seasonality_prior_scale=1.0,
        n_forecast_days=60,
    ),

    "flexible": ProphetModelConfig(
        changepoint_prior_scale=0.3,
        seasonality_prior_scale=15.0,
        seasonality_mode="multiplicative",
        n_forecast_days=120,
    ),

    "long_range": ProphetModelConfig(
        changepoint_prior_scale=0.05,
        n_forecast_days=365,
        interval_width=0.95,
    ),
}
"""
Named preset configurations for common forecasting scenarios.

    'default'      — Prophet defaults, 90-day horizon.
    'conservative' — Tight changepoints, resistant to overfitting short spikes.
    'flexible'     — High changepoint flexibility + multiplicative seasonality,
                     good for fast-growing repos with viral events.
    'long_range'   — 1-year forecast with wider 95% credible intervals.
"""


if __name__ == "__main__":
    # Quick sanity check — verify configs construct and serialize without error
    for name, cfg in CONFIGS.items():
        kwargs = cfg.to_prophet_kwargs()
        print(f"{name:12s}  {cfg}")
