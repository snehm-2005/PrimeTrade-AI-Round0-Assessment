# Market Sentiment vs Trader Performance on Hyperliquid

> How does the market's **Fear / Greed** mood relate to the way traders behave and perform on **Hyperliquid**?
> This project merges daily Fear & Greed sentiment with ~211K historical trade records, measures performance
> and risk behaviour under each sentiment regime, and turns the patterns into simple, testable strategy ideas.

## 1. Project Overview

**Business problem:** analyse how market sentiment (Fear / Greed) relates to trader behaviour and performance
on Hyperliquid, and uncover patterns that could inform smarter trading strategies.

**Questions this project answers**

- Do traders earn more during Fear or Greed periods?
- Do they trade differently (direction, size, aggression, frequency) as sentiment changes?
- Are they more accurate, and do they suffer deeper drawdowns, in some regimes?
- Which coins and times of day work best under which sentiment?
- Do different trader types (high/low risk, frequent/infrequent, consistent/inconsistent) respond differently?

Sentiment is used with its five classes: **Extreme Fear, Fear, Neutral, Greed, Extreme Greed**.
(The bar charts below list classes alphabetically, as produced by `groupby`.)

---

## 2. Datasets

| Dataset | File | Rows | Columns | Description |
|---|---|---|---|---|
| Fear & Greed Index | `fear_greed_index.csv` | 2,644 | 4 | Daily sentiment: `timestamp`, `value`, `classification`, `date` (starts 2018-02-01) |
| Hyperliquid trades | `historical_data.csv` | 211,224 | 16 | One row per fill: `Account`, `Coin`, `Execution Price`, `Size Tokens`, `Size USD`, `Side`, `Timestamp IST`, `Start Position`, `Direction`, `Closed PnL`, `Transaction Hash`, `Order ID`, `Crossed`, `Fee`, `Trade ID`, `Timestamp` |


## 3. Data Preparation and Feature Engineering

1. **Isolate realised outcomes.** Grouping every fill per trader would not give accurate closed PnL, so only rows
   that *close* a position were kept: `Close Long`, `Close Short`, `Liquidated Isolated Short`,
   `Auto-Deleveraging`, `Settlement` &rarr; **84,701 closed-trade rows** (`closed_df`).
2. **Separate position flips.** `Long > Short` and `Short > Long` rows &rarr; **127 rows** (`flips_df`), analysed on their own.
3. **Net PnL.** `net_pnl = Closed PnL - Fee`, plus boolean `is_win` / `is_loss` flags.
4. **Align at daily level.** `Timestamp IST` is parsed (day-first) and normalised to a date; the sentiment `date`
   is parsed and normalised the same way; both trade sets are **left-joined** to the sentiment classification on `date`.
5. **Trader-level and trader x sentiment tables** (`traders_df`, `trader_sentiment_df`) are built for segmentation.
6. The cleaned closed-trade table is exported to `Closed_Trades.csv`.

### Metrics used

| Metric | Definition |
|---|---|
| Net PnL | `Closed PnL - Fee` for each closed trade |
| Win rate | Share of closed trades with `net_pnl > 0` |
| Daily PnL per trader | Net PnL summed per account per day, then averaged per account |
| Trade size (leverage proxy) | Mean `Size USD`. Margin is not available, so size is used as a proxy for risk / leverage |
| Long ratio | Share of closed trades whose `Direction` contains "Long" |
| Aggression | Mean of `Crossed` (share of orders that crossed the spread, i.e. taker orders) |
| Drawdown proxy | Running peak of an account's cumulative net PnL minus its current cumulative net PnL |
| Trade count | Number of closed-trade rows per group |

**Trade-size distribution (`Size USD`, closed trades):** median about 644 USD, mean about 6,638 USD,
75th percentile about 2,223 USD, maximum about 3.9 million USD, so a small number of very large trades stretch the average.

---

## 4. Analysis and Findings
### 4.1 Sentiment vs Trader Performance

#### Average PnL

<p align="center">
  <img src="charts and plots\01_avg_pnl_vs_sentiment.png" alt="Average net PnL per closed trade vs market sentiment" width="700">
  <br><sub><b>Average net PnL per closed trade vs market sentiment</b></sub>
</p>


- **Fear** has the highest average net PnL (about **125 USD** per closed trade), followed by **Extreme Fear** (about 94 USD).
- **Greed** (about 70 USD) and **Neutral** (about 67 USD) sit in the middle.
- **Extreme Greed** is the lowest (about **45 USD**).
- Traders made more per trade when the market was fearful than when it was euphoric.

#### Win rate

<p align="center">
  <img src="charts and plots\04_winrate_vs_sentiment.png" alt="Win rate vs market sentiment" width="700">
  <br><sub><b>Win rate vs market sentiment</b></sub>
</p>


| Sentiment | Approx. win rate |
|---|---|
| Fear | 87% |
| Extreme Greed | 87% |
| Neutral | 83% |
| Extreme Fear | 80% |
| Greed | 75% |

- Trades on **Fear** days win more often than trades on **Greed** days (about 87% vs 75%).
- **Extreme Greed** matches Fear on win rate yet has the lowest average PnL, which suggests many *small* wins
  (consistent with the smallest average trade size, see 4.2).

#### Drawdown

<p align="center">
  <img src="charts and plots\05_drawdown_vs_sentiment.png" alt="Average drawdown vs market sentiment" width="700">
  <br><sub><b>Average drawdown vs market sentiment</b></sub>
</p>


- Average drawdown is by far the largest on **Greed** days (about **30,000 USD**), roughly double Extreme Fear
  (about 14,000 USD) and several times Fear (about 6,000 USD), Extreme Greed (about 5,000 USD) and Neutral (about 4,000 USD).
- Greed regimes are where traders have historically given back the most from their equity peaks.

### 4.2 Sentiment vs Trader Behaviour

#### Long vs short preference

<p align="center">
  <img src="charts and plots\02_long_short_ratio_vs_sentiment.png" alt="Share of long positions vs market sentiment" width="700">
  <br><sub><b>Share of long positions vs market sentiment</b></sub>
</p>


| Sentiment | Long ratio |
|---|---|
| Extreme Fear | about 0.67 |
| Fear | about 0.65 |
| Neutral | about 0.63 |
| Extreme Greed | about 0.53 |
| Greed | about 0.41 |

- In **Fear / Extreme Fear** traders are mostly **long** (0.65 - 0.67), buying weakness. Those are also the regimes with
  the highest average PnL, so this dip-buying behaviour has been working.
- In **Greed** traders lean **short** (about 41% long) but earn only moderate PnL, so shorting greed has been less rewarding.
- **Extreme Greed** is mixed (about 53% long).

#### Aggression

<p align="center">
  <img src="charts and plots\03_aggression_vs_sentiment.png" alt="Aggression (share of crossed/taker orders) vs market sentiment" width="700">
  <br><sub><b>Aggression (share of crossed/taker orders) vs market sentiment</b></sub>
</p>


- Aggression stays in a narrow band (about 0.56 - 0.65). Traders are slightly more aggressive on **Neutral** and **Fear**
  days and least aggressive on **Greed** days, but the differences are small.

#### Trade size

<p align="center">
  <img src="charts and plots/06_trade_size_vs_sentiment.png" alt="Average trade size (USD) vs market sentiment" width="700">
  <br><sub><b>Average trade size (USD) vs market sentiment</b></sub>
</p>


- Average trade size is largest on **Fear** days (about **8,900 USD**) and smallest on **Extreme Greed** days
  (about **3,500 USD**). Greed (about 6,600), Neutral (about 6,100) and Extreme Fear (about 5,900) sit in between.
- Traders size up when the market is fearful and pull back when it is euphoric.

#### Trading activity

<p align="center">
  <img src="charts and plots/07_num_trades_vs_sentiment.png" alt="Number of closed trades vs market sentiment" width="700">
  <br><sub><b>Number of closed trades vs market sentiment</b></sub>
</p>


- **Fear** days see the most closed trades (about 26,500), then Greed (about 19,400), Neutral (about 15,800),
  Extreme Greed (about 13,700) and **Extreme Fear** (about 9,400, the fewest).
- Counts are totals and are not normalised by the number of days in each sentiment class.

### 4.3 Position Flips

Trades that flip a position (`Long > Short` or `Short > Long`) are rare (127 rows) but large. Average net PnL per flip:

| Sentiment | Avg net PnL per flip (USD) |
|---|---|
| Extreme Fear | -1,057.60 |
| Fear | 626.30 |
| Greed | 67.53 |
| Extreme Greed | 53.06 |
| Neutral | 18.72 |

Flips were profitable on average in every regime except **Extreme Fear**, where a few large losing flips dominate.
With only 127 observations, treat this as indicative only.

### 4.4 Coin-Level Insights

#### Win rate by coin and sentiment (top 8 coins by trade count)

<p align="center">
  <img src="charts and plots/08_winrate_heatmap_coin_sentiment.png" alt="Win-rate heatmap: top 8 coins x market sentiment" width="700">
  <br><sub><b>Win-rate heatmap: top 8 coins x market sentiment</b></sub>
</p>


- **kPEPE:** about 100% win rate on Extreme Fear days but collapses to about **7% on Neutral** and **12% on Greed** days.
- **kBONK:** no closed trades on Extreme Fear days; 100% win rate on Fear days, but about 47% on Neutral and only **10% on Greed**.
- **SOL:** steady at about 90% on Fear, Neutral and Greed days.
- **MELANIA:** about 99 - 100% on Extreme Fear, Fear and Neutral days, dropping to 50% on Extreme Greed.
- **ETH:** about **99% on Extreme Fear** days, but only 57% on Greed days.
- **FARTCOIN:** weak on Extreme Fear days (about 16%), strong on Extreme Greed days (about 96%).

#### Long vs short PnL by coin

<p align="center">
  <img src="charts and plots/11_coin_long_vs_short_pnl.png" alt="Average net PnL per coin: long vs short" width="700">
  <br><sub><b>Average net PnL per coin: long vs short</b></sub>
</p>


- **SOL** and **ETH** earn the most from **short** trades (about 540 - 550 USD average). ETH longs are slightly negative.
- **BTC** and **FARTCOIN** *lose* money on shorts (small for BTC, about -65 USD for FARTCOIN).
- On the long side, **SOL**, **BTC** and **kBONK** perform best, while ETH longs are the only losing long side among the top coins.

### 4.5 Time-Based Patterns

#### Time of day (IST)

<p align="center">
  <img src="charts and plots/09_hourly_activity_winrate.png" alt="Hourly trade activity and win rate (IST)" width="700">
  <br><sub><b>Hourly trade activity and win rate (IST)</b></sub>
</p>


- Win rate **peaks around 09:00 (about 95%) and 18:00 (about 94%)** IST, with further highs near 01:00 and 11:00 (about 90%).
- **12:00 - 16:00** and **20:00 - 23:00** IST are consistently above 80%.
- Dips (about 74 - 75%) appear at **04:00, 10:00 and 17:00**.
- Activity is heaviest in the evening and overnight (peaks at 19:00 and 01:00 IST).

#### Monthly volume vs PnL

<p align="center">
  <img src="charts and plots/10_monthly_volume_vs_pnl.png" alt="Monthly trade volume vs net PnL" width="700">
  <br><sub><b>Monthly trade volume vs net PnL</b></sub>
</p>


- Activity is small until late 2024, then **explodes from December 2024 to April 2025**, with closed-trade volume peaking
  at about 23,600 trades in April 2025.
- Monthly net PnL peaks in **February - March 2025** (about 2.1 - 2.2 million USD per month) and eases in April even as volume keeps rising.
- Only a few months are (slightly) negative, for example August and November 2024.
- Volume and profitability rise together, but this does not prove that higher activity *causes* higher profits.

### 4.6 Trader Segments

Every trader was labelled using a **median split** on three characteristics:

| Segment | Rule |
|---|---|
| High Risk / Low Risk | Average trade size above / below the median |
| Frequent / Infrequent | Average trades per active day above / below the median |
| Inconsistent / Consistent | Standard deviation of PnL above / below the median |

| Segment | Avg PnL per trade (USD) | Win rate |
|---|---|---|
| High Risk | 158.81 | 81.3% |
| Low Risk | 118.96 | 86.0% |
| Frequent | 168.20 | 84.8% |
| Infrequent | 109.57 | 82.5% |
| Inconsistent | 228.65 | 80.7% |
| Consistent | 49.12 | 86.6% |

#### Risk: high vs low

<table>
  <tr>
    <td align="center" width="50%"><img src="charts and plots/12_performance_high_vs_low_risk.png" alt="Average PnL: high-risk vs low-risk traders" width="100%"><br><sub><b>Average PnL: high-risk vs low-risk traders</b></sub></td>
    <td align="center" width="50%"><img src="charts and plots/13_winrate_high_vs_low_risk.png" alt="Win rate: high-risk vs low-risk traders" width="100%"><br><sub><b>Win rate: high-risk vs low-risk traders</b></sub></td>
  </tr>
</table>


- High-risk (larger-size) traders earn **more per trade** but win **less often** than low-risk traders.

#### Frequency: frequent vs infrequent

<table>
  <tr>
    <td align="center" width="50%"><img src="charts and plots/14_performance_frequent_vs_infrequent.png" alt="Average PnL: frequent vs infrequent traders" width="100%"><br><sub><b>Average PnL: frequent vs infrequent traders</b></sub></td>
    <td align="center" width="50%"><img src="charts and plots/15_winrate_frequent_vs_infrequent.png" alt="Win rate: frequent vs infrequent traders" width="100%"><br><sub><b>Win rate: frequent vs infrequent traders</b></sub></td>
  </tr>
</table>


- Frequent traders earn more on average, but infrequent traders win almost as often, so **trading more does not by itself make traders more accurate**.

#### Consistency: consistent vs inconsistent

<table>
  <tr>
    <td align="center" width="50%"><img src="charts and plots/16_performance_consistent_vs_inconsistent.png" alt="Average PnL: consistent vs inconsistent traders" width="100%"><br><sub><b>Average PnL: consistent vs inconsistent traders</b></sub></td>
    <td align="center" width="50%"><img src="charts and plots/17_winrate_consistent_vs_inconsistent.png" alt="Win rate: consistent vs inconsistent traders" width="100%"><br><sub><b>Win rate: consistent vs inconsistent traders</b></sub></td>
  </tr>
</table>


- Inconsistent traders have the higher average PnL (big swings), but **consistent traders win more often**.

### 4.7 Segments Across Sentiment

Segments were recomputed per trader and per sentiment class to see who does well in which regime.

#### Risk segment x sentiment

<p align="center">
  <img src="charts and plots/18_performance_risk_segment_sentiment.png" alt="Average PnL by risk segment and sentiment" width="700">
  <br><sub><b>Average PnL by risk segment and sentiment</b></sub>
</p>


- **High-risk** traders shine on **Greed** (about 660 USD) and **Extreme Fear** (about 515 USD) days, and do well on Neutral
  (about 340 USD), but earn very little on **Extreme Greed** days (about 25 USD).
- **Low-risk** traders are positive on Extreme Fear, Fear, Greed and Extreme Greed but **lose money on Neutral** days (about -55 USD).

#### Frequency segment x sentiment

<p align="center">
  <img src="charts and plots/19_performance_frequency_sentiment.png" alt="Average PnL by trading-frequency segment and sentiment" width="700">
  <br><sub><b>Average PnL by trading-frequency segment and sentiment</b></sub>
</p>


- **Infrequent** traders earn the most on **Extreme Fear** (about 605 USD), **Greed** (about 430 USD) and **Neutral** (about 230 USD) days,
  but **lose money on Fear** days (about -12 USD).
- **Frequent** traders are profitable in every regime and do comparatively best on Fear (about 150 USD) and Greed (about 265 USD) days.

---

## 5. Key Takeaways

| Question | Finding |
|---|---|
| Do traders earn more in Fear or Greed? | **Fear** gives the highest average PnL; **Extreme Greed** the lowest. |
| Do they trade differently? | Longer bias and larger size in Fear; shorter bias and smaller size in Greed / Extreme Greed. |
| Are they more accurate? | Win rate is highest on Fear (and Extreme Greed) days and lowest on Greed days. |
| Where is the risk? | **Greed** days have by far the deepest average drawdowns. |
| Do they trade more in some regimes? | Yes, most trades happen on Fear days; fewest on Extreme Fear days. |
| Do coins behave differently? | Yes. Coin win rates swing widely with sentiment (kPEPE, kBONK, ETH, FARTCOIN). |
| Does time of day matter? | Win rate peaks around 09:00 and 18:00 IST and dips at 04:00, 10:00 and 17:00 IST. |
| Who does best? | High-risk and inconsistent traders earn more per trade; low-risk and consistent traders win more often. |

---

## 6. Strategy Ideas

**Strategy 1 - Adjust size by risk profile**
- Low-risk traders lose money on **Neutral** days, so they should place more of their trades on Greed, Fear or Extreme Fear days.
- High-risk traders perform poorly on **Extreme Greed** days, so they should avoid large-size trades then.

**Strategy 2 - Adjust activity by trading frequency**
- Infrequent traders lose money on **Fear** days and outperform on Extreme Fear, Greed and Neutral days, so they should
  trade more in those regimes and avoid Fear days.
