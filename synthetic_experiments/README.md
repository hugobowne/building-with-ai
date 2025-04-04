# Statistical Distributions Educational Notebooks

This project contains educational Jupyter notebooks about various probability distributions, focusing on real-world examples, data generating processes, and visualizations.

## Project Structure

```
synthetic_experiments/
├── requirements.txt    # Project dependencies
└── statistics/         # Directory containing distribution notebooks
    ├── binomial.ipynb  # Binomial distribution notebook
    ├── poisson.ipynb   # Poisson distribution notebook
    ├── exponential.ipynb # Exponential distribution notebook
    ├── gaussian.ipynb  # Gaussian/Normal distribution notebook
    └── beta.ipynb      # Beta distribution notebook
```

## Notebook Structure

Each notebook follows this structure:

1. **Real-world Examples**
   - 3-5 concrete examples where this distribution naturally occurs
   - Visualizations of real datasets showing this pattern

2. **Data Generating Process**
   - Explanation of the underlying random process
   - Step-by-step simulations of how data is generated
   - Introduction to mathematical notation

3. **Implementation & Visualization**
   - NumPy random sampling code
   - Seaborn visualizations (histograms, KDEs, ECDFs, swarm plots)
   - Parameter exploration with interactive widgets

## Distribution-Specific Content

### 1. Binomial Distribution
- **Examples**: Coin flips, A/B testing, quality control sampling
- **Focus**: Success/failure trials, parameter effects (n, p)
- **Visualizations**: Probability mass function, cumulative distribution function

### 2. Poisson Distribution
- **Examples**: Customer arrivals, website traffic, rare events
- **Focus**: Rate parameter, relationship to exponential
- **Visualizations**: Probability mass function, parameter effects

### 3. Exponential Distribution
- **Examples**: Service times, equipment failures, radioactive decay
- **Focus**: Memoryless property, relationship to Poisson
- **Visualizations**: Probability density function, cumulative distribution function

### 4. Gaussian/Normal Distribution
- **Examples**: Measurement errors, heights, test scores
- **Focus**: Central Limit Theorem, parameter effects
- **Visualizations**: Probability density function, Q-Q plots

### 5. Beta Distribution
- **Examples**: Conversion rates, proportions, Bayesian priors
- **Focus**: Shape parameters, conjugate priors
- **Visualizations**: Probability density function, parameter effects

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Launch Jupyter:
   ```
   jupyter notebook
   ```

3. Navigate to the statistics directory and open any notebook
