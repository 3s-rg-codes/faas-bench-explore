# Serverless Secrets – Data Analysis Repository

This repository contains all data analysis conducted for the *"Serverless Secrets"* paper. In addition to the figures presented in the paper, it includes intermediate analysis steps, exploratory visualizations, and supplementary experiments that contributed to the final results.

## Setup

To reproduce the figures:

1. Add the required database(s) to the repository. 
TODO add where databases can be found
2. Open the desired notebook(s).
3. Run the first cell in each notebook to initialize the database connection.
4. Remaining cells are designed, so they can be executed individually, and no order is required.

**Note:**  
The data for the *geodistribution experiment* is stored in a separate database from the other experiments.

## Notebooks Overview

The notebooks are organized by experiment:

### 00 – Elasticity
- Analyzes system performance under sustained load.
- Load pattern: gradual ramp-up followed by ramp-down.

### 01 – Cold Start Experiment
- Evaluates platform behavior during cold starts.
- Aggregations:
  - Per day
  - Per weekday
  - Per hour
  - Overall
- Includes analysis of:
  - Tail latencies
  - Cross-platform correlations

### 02 – Warm Start Experiment
- Evaluates platform behavior during warm starts.
- Same aggregation dimensions as the cold start experiment.
- Includes correlation analysis between platforms and latency behavior.

### 03 – I/O Consistency Experiment
- Analyzes I/O performance consistency across platforms.
- Reports:
  - Daily aggregated metrics
  - Error rates over the full experiment duration

### 04 – CPU Consistency Experiment
- Evaluates CPU performance consistency.
- Reports:
  - Daily and overall aggregated metrics
  - Error rates
- Includes combined CPU and I/O analysis to explore potential correlations.

### 05 – Data Transfer Experiment
- Analyzes data transfer latency across platforms.
- Investigates:
  - Correlation between cold starts and transfer latency
  - Producer–consumer behavior
  - Cross-platform interactions

### 06 – General Data Exploration
- Contains sanity checks and exploratory analysis.
- Used to validate data integrity and detect anomalies.

### 07 – Geodistribution Experiment
- Analyzes latency in a geographically distributed setup.
- Aggregations:
  - Daily metrics over the experiment duration
  - Overall metrics

### 08 – Aggregated Metrics
- Provides a high-level overview of all platforms.
- Used to identify inconsistencies or unusual behavior across providers.