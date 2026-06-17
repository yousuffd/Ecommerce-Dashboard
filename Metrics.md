# Metrics Calculation Reference

**Electronic Commerce Intelligence — C-Suite Dashboard**

This document defines every metric computed by the dashboard, covering its business meaning, the data columns it depends on, and the exact calculation logic.

---

## 1. Core Revenue Metrics

### Total Revenue
**Definition:** Sum of net order revenue across all orders in the selected period.

**Required columns:** `revenue`

**Calculation:** Sum of the `revenue` column across all rows. If `revenue` is absent, it is derived as `unit_price × quantity` with a warning displayed.

---

### Average Order Value (AOV)
**Definition:** The average net revenue generated per unique order. A key indicator of basket size and pricing effectiveness.

**Required columns:** `revenue`, `order_id`

**Calculation:** `Total Revenue ÷ Number of unique order_ids`

---

### MoM Revenue Growth
**Definition:** Month-over-Month percentage change in revenue, comparing the most recent complete month against the immediately preceding month. Used to assess short-term momentum.

**Required columns:** `revenue`, `order_date`

**Calculation:**
1. Group revenue by calendar month (derived from `order_date`).
2. Sort months ascending.
3. `MoM Growth (%) = ((Revenue_last_month − Revenue_prev_month) ÷ Revenue_prev_month) × 100`

Returns 0.0 if fewer than two months of data are available.

---

### QoQ Revenue Growth
**Definition:** Quarter-over-Quarter percentage change in revenue, comparing the most recent quarter against the prior quarter.

**Required columns:** `revenue`, `order_date`

**Calculation:**
1. Group revenue by calendar quarter.
2. Sort quarters ascending.
3. `QoQ Growth (%) = ((Revenue_last_quarter − Revenue_prev_quarter) ÷ Revenue_prev_quarter) × 100`

Returns 0.0 if fewer than two quarters of data are available.

---

### Revenue Concentration (Top-3 Products)
**Definition:** Percentage of total revenue attributable to the top three products by revenue. A high concentration signals SKU dependency risk.

**Required columns:** `revenue`, `product_name`

**Calculation:**
1. Sum revenue per product.
2. Identify the top 3 products by descending revenue.
3. `Revenue Concentration (%) = (Sum of top-3 product revenues ÷ Total Revenue) × 100`

---

### Revenue at Risk
**Definition:** Total revenue value of orders currently in an unresolved, in-flight state — not yet delivered and not yet cancelled or returned. Represents potential revenue that could be lost to returns, cancellations, or fulfilment failures.

**Required columns:** `revenue`, `order_status`

**Calculation:** Sum of `revenue` for all orders where `order_status` is one of: `processing`, `shipped`, or `in transit` (case-insensitive).

---

## 2. Operational Metrics

### Perfect Order Rate
**Definition:** The percentage of orders that were delivered, on time, and not returned or refunded. The single most comprehensive measure of end-to-end fulfilment quality.

**Required columns:** `order_status`, `shipping_days`, `order_id`

**Derived flags (row-level):**
- `is_delivered` = `order_status` (lowercased) == `"delivered"`
- `is_delayed` = `shipping_days > 7`
- `is_returned` = `order_status` (lowercased) is one of `"returned"` or `"refunded"`
- `is_perfect` = `is_delivered AND NOT is_delayed AND NOT is_returned`

**Calculation:** `Perfect Order Rate (%) = (Count of rows where is_perfect is True ÷ Total rows) × 100`

Benchmark: 75%+ is considered industry-acceptable.

---

### Refund / Return Rate
**Definition:** Percentage of orders that ended in a return or refund. An elevated rate signals product quality, mismatch, or logistics issues.

**Required columns:** `order_status`

**Calculation:** `Refund Rate (%) = (Count of orders where is_returned is True ÷ Total orders) × 100`

Where `is_returned` = `order_status` (lowercased) is `"returned"` or `"refunded"`.

---

### Cancellation Rate
**Definition:** Percentage of orders cancelled before fulfilment. Cancellations indicate demand-side issues such as price dissatisfaction, delivery ETAs, or stock problems.

**Required columns:** `order_status`

**Calculation:** `Cancel Rate (%) = (Count of orders where is_cancelled is True ÷ Total orders) × 100`

Where `is_cancelled` = `order_status` (lowercased) is `"cancelled"` or `"canceled"`.

---

### Delay Rate
**Definition:** Percentage of orders that took more than 7 days to ship. Used as a proxy for logistics performance when promised delivery dates are unavailable.

**Required columns:** `shipping_days`

**Calculation:** `Delay Rate (%) = (Count of orders where shipping_days > 7 ÷ Total orders) × 100`

---

### SLA Breach Rate
**Definition:** Percentage of orders where the actual delivery date exceeded the promised delivery date. More precise than delay rate when delivery date commitments are recorded.

**Required columns:** `promised_delivery_date`, `actual_delivery_date`

**Calculation:** `SLA Breach Rate (%) = (Count of orders where actual_delivery_date > promised_delivery_date ÷ Total orders) × 100`

**Fallback:** If either date column is missing, `sla_breach` defaults to `is_delayed` (shipping_days > 7).

---

### Average Shipping Days
**Definition:** Mean number of days between order placement and delivery across all orders.

**Required columns:** `shipping_days`

**Calculation:** Arithmetic mean of the `shipping_days` column.

---

### Shipping Speed Bands
**Definition:** Distribution of orders across four delivery speed categories, used in the Operations page shipping donut chart.

**Required columns:** `shipping_days`

| Band | Days |
|---|---|
| Express | 0–2 days |
| Standard | 3–4 days |
| Slow | 5–6 days |
| Delayed | 7+ days |

**Calculation:** `shipping_days` is binned using `pd.cut` with thresholds `[-1, 2, 4, 6, 9999]` so that same-day orders (0 days) are captured in the Express band.

---

## 3. Customer Metrics

These metrics are only computed when a `customer_id` column is present.

### Unique Customers
**Definition:** Count of distinct customers with at least one order.

**Required columns:** `customer_id`

**Calculation:** `customer_id.nunique()`

---

### Repeat Purchase Rate
**Definition:** Percentage of customers who placed more than one order. A leading indicator of loyalty and product-market fit.

**Required columns:** `customer_id`, `order_id`

**Calculation:**
1. Count unique `order_id` per `customer_id`.
2. `Repeat Rate (%) = (Count of customers with order_count > 1 ÷ Total unique customers) × 100`

---

### Customer Lifetime Value (LTV)
**Definition:** Average total revenue generated per customer over the full dataset period. A simplified LTV used as a directional benchmark rather than a projected model.

**Required columns:** `revenue`, `customer_id`

**Calculation:** `LTV = Total Revenue ÷ Unique Customers`

---

## 4. Profitability Metrics

These metrics are only computed when the relevant cost columns are present.

### Gross Margin (Total)
**Definition:** Total gross profit: revenue minus cost of goods sold.

**Required columns:** `gross_margin` (pre-computed) or `cogs`

**Calculation:** Sum of the `gross_margin` column.

If `gross_margin` is not provided but `cogs` is, gross margin per row can be derived as `revenue − cogs`.

---

### Gross Margin %
**Definition:** Gross profit as a percentage of revenue. Measures the efficiency of production and pricing.

**Required columns:** `gross_margin`, `revenue`

**Calculation:** `Gross Margin % = (Total Gross Margin ÷ Total Revenue) × 100`

---

### Discount Rate
**Definition:** Percentage of orders where a discount was applied.

**Required columns:** `discount_amount`

**Calculation:** `Discount Rate (%) = (Count of orders where discount_amount > 0 ÷ Total orders) × 100`

---

### Average Discount Depth
**Definition:** Among discounted orders, the average discount as a percentage of the original unit price.

**Required columns:** `discount_amount`, `unit_price`

**Row-level derived column:** `discount_pct = (discount_amount ÷ unit_price) × 100`

**Calculation:** Mean of `discount_pct` across all rows where `discount_amount > 0`.

---

### Revenue Lost to Discounts
**Definition:** Total monetary value of discounts given across all orders. Quantifies the top-line cost of promotional activity.

**Required columns:** `discount_amount`

**Calculation:** Sum of the `discount_amount` column.

---

## 5. Composite Business Health Score

**Definition:** A single 0–100 score summarising overall business health across five operational and financial dimensions. Designed for executive-level at-a-glance status.

**Required columns:** All columns needed by Perfect Order Rate, Refund Rate, Cancellation Rate, Delay Rate, and MoM Growth (see above).

**Component weights and sub-scores:**

| Component | Weight | Sub-score Logic |
|---|---|---|
| Perfect Order Rate | 30% | `min(perfect_order_rate ÷ 85, 1) × 100` — benchmarked against 85% ceiling |
| Refund Rate | 25% | `max(0, (10 − refund_rate) ÷ 10) × 100` — penalises refund rates above 10% |
| Cancellation Rate | 20% | `max(0, (5 − cancel_rate) ÷ 5) × 100` — penalises cancel rates above 5% |
| MoM Revenue Growth | 15% | `min(max(mom_growth + 10, 0) ÷ 20, 1) × 100` — centred at 0%, tolerates −10% decline |
| Delay Rate | 10% | `max(0, (25 − delay_rate) ÷ 25) × 100` — penalises delay rates above 25% |

**Final score:** `Health Score = Σ (sub-score × weight)`, rounded to one decimal place.

**Interpretation:**

| Score | Status | Display colour |
|---|---|---|
| 75–100 | Healthy | Green |
| 50–74 | Needs attention | Amber/Gold |
| 0–49 | At risk | Red |

---

## 6. Derived Row-Level Columns

The following boolean and numeric columns are computed per-row during the data processing step and feed into the aggregate metrics above.

| Column | Derivation |
|---|---|
| `month` | `order_date` truncated to month period |
| `week` | `order_date` truncated to week period |
| `quarter` | `order_date` truncated to quarter period |
| `year` | Calendar year from `order_date` |
| `is_returned` | `order_status` ∈ `{returned, refunded}` |
| `is_cancelled` | `order_status` ∈ `{cancelled, canceled}` |
| `is_delivered` | `order_status` == `delivered` |
| `is_delayed` | `shipping_days > 7` |
| `is_express` | `shipping_days ≤ 2` |
| `is_perfect` | `is_delivered AND NOT is_delayed AND NOT is_returned` |
| `sla_breach` | `actual_delivery_date > promised_delivery_date` (falls back to `is_delayed`) |
| `aov` | `revenue ÷ max(quantity, 1)` |
| `margin_pct` | `gross_margin ÷ max(revenue, 0.01) × 100` |
| `discount_pct` | `discount_amount ÷ max(unit_price, 0.01) × 100` |
| `is_discounted` | `discount_amount > 0` |

---

## 7. Notes on Data Quality Handling

- Rows with unparseable `order_date` values are dropped with a warning shown in the UI.
- Numeric columns (`quantity`, `unit_price`, `revenue`, `shipping_days`) that cannot be parsed are coerced to 0 rather than dropped.
- If `revenue` sums to zero but `unit_price` is non-zero, revenue is silently derived as `unit_price × quantity` with a warning.
- All column names are normalised to lowercase with underscores before processing, making the schema tolerant of variations in source file formatting.
- Missing optional columns result in the corresponding metrics being set to `None` and hidden from the UI rather than causing errors.
