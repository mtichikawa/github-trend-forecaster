"""Smoke tests: package imports cleanly."""


def test_data_collector_imports():
    from src import data_collector  # noqa: F401


def test_models_package_imports():
    from src import models  # noqa: F401


def test_prophet_model_imports():
    from src.models import prophet_model  # noqa: F401
    from src.models.prophet_model import ProphetModelConfig, CONFIGS

    assert "default" in CONFIGS
    assert isinstance(CONFIGS["default"], ProphetModelConfig)
