# GitHub Repository Trend Forecaster

Predict future growth of GitHub repositories using time series forecasting.

## Features

- Automatic data collection from GitHub API
- Facebook Prophet forecasting model
- Trend and seasonality analysis
- Interactive visualizations
- "Rising star" detection

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run example
python examples/quick_start.py
```

## Usage

```python
from src.data_collector import GitHubDataCollector
from src.models.prophet_forecast import RepoForecaster

# Collect data
collector = GitHubDataCollector()
collector.save_data('pytorch', 'pytorch')

# Forecast
forecaster = RepoForecaster()
data = forecaster.load_data('pytorch_pytorch')
df = forecaster.prepare_data(data)
forecaster.train(df)
forecast = forecaster.predict(periods=90)

# Visualize
forecaster.plot_forecast('pytorch/pytorch')
```

## What I Learned

- Time series forecasting with Prophet
- Working with GitHub API and rate limiting
- Handling sparse time series data
- Visualization of predictions with uncertainty

Contact: Mike Ichikawa - projects.ichikawa@gmail.com

# Updated: 2025-08-15
# Updated: 2025-10-15
# Updated: 2025-10-19
# Updated: 2025-10-27
# Updated: 2025-11-20
# Updated: 2025-12-05
# Updated: 2026-02-03
# Updated: 2026-02-15