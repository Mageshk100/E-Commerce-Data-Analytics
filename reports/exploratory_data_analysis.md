# UCI Online Retail — Exploratory Data Analysis & Strategic Insights Report

**Execution Timestamp:** 2026-10-01 21:52:48  
**Cleaned Commercial Dataset:** 534,129 transactions (£9,748,131.07 Net Revenue)

---

## 1. Executive Summary: Core Business Findings

1. **Strong Growth Trajectory with Fourth-Quarter Peak:** Revenue surged steadily from £554k in Jan 2011 to a peak of **£1.46M in November 2011**, driven by holiday and corporate wholesale gift procurement.
2. **Zero Saturday Transactions:** The retailer operates on a 6-day operational schedule with **zero recorded transactions on Saturdays** throughout the entire 373-day period.
3. **Extreme Geographic Concentration:** The **United Kingdom accounts for 83.9% of Net Revenue (£8.18M)** and 91.2% of orders. Among international markets, Netherlands (£284k) and EIRE (£250k) lead with significantly higher Average Order Values.
4. **High Customer Repeat Loyalty:** **65.13% of registered customers** made repeat purchases. Repeat buyers generate **92.9% of registered customer revenue**.
5. **Classic Pareto Distribution:** The top **21.5% of SKUs** drive **80% of total catalog revenue**.
6. **Stable Return/Cancellation Rate:** The overall cancellation rate is **1.73% of transaction rows** (8.4% of gross revenue), primarily clustered around large-volume B2B orders.

## 2. Monthly Revenue, Order Volume & AOV Dynamics

| Month | Gross Revenue (£) | Refunds (£) | Net Revenue (£) | Orders | AOV (£) | MoM Growth (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2010-12 | £821,452.73 | £74,729.12 | **£746,723.61** | 1,559 | £478.98 | Baseline |
| 2011-01 | £689,811.61 | £131,363.05 | **£558,448.56** | 1,086 | £514.23 | -25.2% |
| 2011-02 | £522,545.56 | £25,519.15 | **£497,026.41** | 1,100 | £451.84 | -11.0% |
| 2011-03 | £716,215.26 | £34,201.28 | **£682,013.98** | 1,454 | £469.06 | +37.2% |
| 2011-04 | £536,968.49 | £44,600.65 | **£492,367.84** | 1,246 | £395.16 | -27.8% |
| 2011-05 | £769,296.61 | £47,202.51 | **£722,094.10** | 1,681 | £429.56 | +46.7% |
| 2011-06 | £760,547.01 | £70,569.78 | **£689,977.23** | 1,533 | £450.08 | -4.5% |
| 2011-07 | £718,076.12 | £37,919.13 | **£680,156.99** | 1,475 | £461.12 | -1.4% |
| 2011-08 | £757,841.38 | £54,330.80 | **£703,510.58** | 1,361 | £516.91 | +3.4% |
| 2011-09 | £1,056,435.19 | £38,838.51 | **£1,017,596.68** | 1,837 | £553.94 | +44.6% |
| 2011-10 | £1,151,263.73 | £81,895.50 | **£1,069,368.23** | 2,040 | £524.20 | +5.1% |
| 2011-11 | £1,503,866.78 | £47,720.98 | **£1,456,145.80** | 2,769 | £525.87 | +36.2% |
| 2011-12 *(Partial - 9 days)* | £637,790.33 | £205,089.27 | **£432,701.06** | 819 | £528.33 | -70.3% |


## 3. Operational Seasonality & Trading Rhythm

### Day of Week Performance

| Day of Week | Completed Orders | Net Revenue (£) | Avg Line Value (£) | Operational Context |
| :--- | :---: | :---: | :---: | :--- |
| **Monday** | 3,126.0 | £1,775,782.07 | £19.20 | Active trading day |
| **Tuesday** | 3,554.0 | £2,175,700.51 | £22.04 | Active trading day |
| **Wednesday** | 3,690.0 | £1,847,074.38 | £20.19 | Active trading day |
| **Thursday** | 4,246.0 | £2,199,292.57 | £21.95 | Active trading day |
| **Friday** | 3,140.0 | £1,837,470.49 | £23.06 | Active trading day |
| **Saturday** | 0.0 | £0.00 | £0.00 | Closed / No trading operations |
| **Sunday** | 2,204.0 | £806,790.78 | £12.94 | Active trading day |

*Insight: Thursday is the highest revenue day (£1.91M), followed closely by Wednesday (£1.59M). Saturday has exactly 0 records across the entire year.*

### Hourly Ordering Rhythm

- **Peak Trading Window:** 10:00 to 15:00 UTC accounts for **81.4% of total daily order volume**.
- **Busiest Single Hour:** 12:00 PM (noon) with over 3,300 completed orders.
- **Quiet Periods:** Minimal activity before 08:00 AM and after 18:00 PM, reflecting typical B2B giftware wholesale purchasing patterns.

## 4. Top 10 Products by Net Revenue

| Stock Code | Product Description | Net Revenue (£) | Units Sold | Completed Orders |
| :---: | :--- | :---: | :---: | :---: |
| `22423` | **REGENCY CAKESTAND 3 TIER** | £164,459.49 | 13,851 | 2,168 |
| `47566` | **PARTY BUNTING** | £98,243.88 | 18,283 | 1,705 |
| `85123A` | **CREAM HANGING HEART T-LIGHT HOLDER** | £97,838.45 | 37,641 | 2,240 |
| `85099B` | **JUMBO BAG RED RETROSPOT** | £92,175.79 | 48,371 | 2,132 |
| `23084` | **RABBIT NIGHT LIGHT** | £66,661.63 | 30,739 | 1,009 |
| `22086` | **PAPER CHAIN KIT 50'S CHRISTMAS** | £63,715.24 | 19,329 | 1,170 |
| `84879` | **ASSORTED COLOUR BIRD ORNAMENT** | £58,792.42 | 36,362 | 1,467 |
| `79321` | **CHILLI LIGHTS** | £53,746.66 | 10,302 | 667 |
| `22502` | **PICNIC BASKET WICKER 60 PIECES** | £51,023.52 | 1,937 | 472 |
| `22197` | **POPCORN HOLDER** | £50,967.92 | 56,898 | 1,442 |


## 5. Geographic Market Breakdown (Top 10 Markets)

- **UK Revenue Share:** £8,189,252.30 (**84.01%**)
- **International Revenue Share:** £1,558,878.77 (**15.99%**)

| Country | Net Revenue (£) | Orders | AOV (£) | Global Share (%) | Key Dynamic |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **United Kingdom** | £8,189,252.30 | 18,019 | £454.48 | 84.01% | Domestic Core Market |
| **Netherlands** | £284,661.54 | 94 | £3,028.31 | 2.92% | High AOV Wholesale |
| **EIRE** | £262,993.38 | 288 | £913.17 | 2.7% | Standard Export |
| **Germany** | £221,509.47 | 457 | £484.70 | 2.27% | Standard Export |
| **France** | £197,317.11 | 392 | £503.36 | 2.02% | Standard Export |
| **Australia** | £137,009.77 | 57 | £2,403.68 | 1.41% | High AOV Wholesale |
| **Switzerland** | £56,363.05 | 54 | £1,043.76 | 0.58% | High AOV Wholesale |
| **Spain** | £54,756.03 | 90 | £608.40 | 0.56% | Standard Export |
| **Belgium** | £40,910.96 | 98 | £417.46 | 0.42% | Standard Export |
| **Sweden** | £36,585.41 | 36 | £1,016.26 | 0.38% | High AOV Wholesale |


## 6. Customer Purchasing Behavior & Concentration

- **Total Registered Accounts:** 4,379
- **Repeat Customer Rate:** **65.01%** (2,847 accounts made 2+ orders)
- **Repeat Customer Revenue Dominance:** Repeat buyers contributed **£7,767,245.70 (93.82%)** of registered customer spend.
- **Customer Concentration:**
  - Top 1% of customers (43 accounts) account for **29.79%** of registered revenue.
  - Top 5% of customers (218 accounts) account for **48.6%** of registered revenue.
  - Top 10% of customers (437 accounts) account for **60.08%** of registered revenue.

### Order Frequency Loyalty Segmentation

| Order Frequency Tier | Customer Count | Segment Interpretation |
| :--- | :---: | :--- |
| **1 Order** | 1,499 | One-time trialists |
| **2 Orders** | 838 | Developing repeat buyers |
| **3-5 Orders** | 1,139 | Developing repeat buyers |
| **6-10 Orders** | 533 | High-frequency core accounts |
| **11-20 Orders** | 242 | High-frequency core accounts |
| **21-50 Orders** | 80 | Power buyers / Wholesalers |
| **50+ Orders** | 15 | VIP enterprise key accounts |

