# New Kids – Data Analysis Repository

This repository contains all data analysis conducted for the *"New Kids"* paper. In addition to the figures presented in the paper, it includes intermediate analysis steps, exploratory visualizations, and supplementary experiments that contributed to the final results.

For experiment setup please refer to https://github.com/3s-rg-codes/faas-bench-explore.

## Setup

To reproduce the figures:

1. Add the required database(s) to the repository: https://doi.org/10.14279/depositonce-25748
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

# Citation

If you use this data or your research, please cite our paper:

```bib
@article{schirmer2026newKids,
    author = {Schirmer, Trever and Wiegand, Aris and di Benedetto, Lucca and Gustafsson, Linus and Carl, Natalie and Pfandzelter, Tobias and Bermbach, David},
    title = {New Kids: An Architecture and Performance Investigation of Second-Generation Serverless Platforms},
    year = {2026},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    issn = {1533-5399},
    url = {https://doi.org/10.1145/3841482},
    doi = {10.1145/3841482},
    note = {Just Accepted},
    journal = {ACM Trans. Internet Technol.},
    month = aug,
    keywords = {Serverless, FaaS, platform architecture, performance comparison}
}
```
