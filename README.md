# Bayberry Data Analytics Dashboard

A comprehensive data analytics dashboard for analyzing purchase and sales data, calculating batch-wise profits, and generating insights.

## Features

- 📊 Batch-wise profit analysis
- 📈 Executive summary with key metrics
- 🔍 Advanced filtering and search
- 📋 Interactive AG Grid table with sorting/filtering
- 💰 Detailed profit breakdown waterfall charts
- 📥 Export to CSV

## Architecture

```
├── src/
│   ├── models/          # Data models (Purchase, Sale, BatchProfit)
│   ├── services/        # Business logic (ExcelReader, DataTransformer, ProfitCalculator)
│   └── utils/           # Utility functions
├── app.py               # Main Streamlit dashboard
├── BayberryStock.xlsx   # Source Excel file
└── requirements.txt     # Python dependencies
```

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Data Structure

### Purchases Sheet
- Links via `BTREFNO` field
- Categories: FG, TR, SV, CO, CG, AD
- Key fields: IN_QTY, IN_RATE

### Sales Sheet
- Links via `Batch No.` field
- Key fields: Sale Qty., Free Qty., OUT_RATE, Discount Value

## Profit Calculation

```
Revenue = Gross Value - Discount Value
Cost = IN_QTY × IN_RATE
Free Goods Loss = Free Qty. × OUT_RATE
Profit = Revenue - Cost - Free Goods Loss
```

## Features

### Executive Summary
- Total batches analyzed
- Total purchase cost
- Total revenue
- Total profit and margin
- Profit/Loss distribution

### Batch-wise Analysis
- Interactive table with 20+ columns
- Filter by status, category, profit range
- Sort and search capabilities
- Select row to view detailed breakdown

### Detailed Breakdown
- Purchase information
- Sales summary
- Profit waterfall chart
- Export to CSV

## Technologies

- **Streamlit**: Dashboard framework
- **AG Grid**: Advanced data table
- **Plotly**: Interactive charts
- **Pandas**: Data processing
- **Python**: Backend logic

## Future Enhancements

- Customer profitability analysis
- Time-series trend analysis
- Product performance tracking
- Cost allocation for SV/CO/CG charges
- Multi-period comparison
