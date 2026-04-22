""" Greed vs Fear — Trader Sentiment Dashboard """

 
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings("ignore")
 
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Greed vs Fear Dashboard",
                   layout="wide", page_icon="📊")
 
# ── Dark plot style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117", "axes.facecolor": "#0d1117",
    "axes.edgecolor": "#30363d", "axes.labelcolor": "#8b949e",
    "xtick.color": "#8b949e", "ytick.color": "#8b949e",
    "text.color": "#e6edf3", "grid.color": "#21262d",
    "grid.linestyle": "--", "grid.alpha": 0.5,
    "legend.facecolor": "#161b22", "legend.edgecolor": "#30363d",
    "font.family": "monospace", "axes.titleweight": "bold",
    "axes.titlecolor": "#e6edf3",
})
 
GREED = "#f97316"; FEAR = "#38bdf8"; GREEN = "#22c55e"
RED = "#ef4444"; GOLD = "#fbbf24"; PURPLE = "#a78bfa"
SENT_ORDER  = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
SENT_COLORS = {"Extreme Fear": "#818cf8", "Fear": FEAR,
               "Neutral": GOLD, "Greed": GREED, "Extreme Greed": RED}
 
@st.cache_data
def load_data():
    df = pd.read_csv("Closed_Trades.csv")
    df["date"]  = pd.to_datetime(df["date"])
    df["hour"]  = pd.to_datetime(df["Timestamp IST"], dayfirst=True).dt.hour
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df
 
df = load_data()
TOP_COINS   = df["Coin"].value_counts().head(8).index.tolist()
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_sentiments = df["classification"].dropna().unique().tolist()
sel_sent = st.sidebar.multiselect("Sentiment", SENT_ORDER,
                                   default=SENT_ORDER)
sel_coins = st.sidebar.multiselect("Coins (plots 3 & 9)", TOP_COINS,
                                    default=TOP_COINS[:8])
n_clusters = st.sidebar.slider("Clusters (archetypes)", 2, 6, 3)
 
df_f = df[df["classification"].isin(sel_sent)]
 
# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("#Greed vs Fear — Trader Sentiment Dashboard")
st.markdown("---")
 
# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Closed Trades",  f"{len(df_f):,}")
k2.metric("Accounts",      df_f["Account"].nunique())
k3.metric("Avg Net PnL",   f"${df_f['net_pnl'].mean():.1f}")
k4.metric("Overall Win Rate", f"{df_f['is_win'].mean()*100:.1f}%")
 
st.markdown("---")
 
st.header("Key Charts")
 
# ── PLOT 1 — Coin × Sentiment Heatmap ─────────────────────────────────────────
st.subheader("Plot 3 · Win Rate Heatmap — Coin × Sentiment")
st.caption("Which coins perform best under which market mood?")
 
coin_sent = (
    df_f[df_f["Coin"].isin(sel_coins)]
    .groupby(["Coin","classification"])["is_win"]
    .mean().unstack()
)
# keep only columns present in filtered data
present_cols = [c for c in SENT_ORDER if c in coin_sent.columns]
coin_sent = coin_sent[present_cols]
 
fig3, ax3 = plt.subplots(figsize=(10, 4))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "rg", [RED, "#21262d", GREEN])
im = ax3.imshow(coin_sent.values, cmap=cmap, aspect="auto", vmin=0, vmax=1)
plt.colorbar(im, ax=ax3, label="Win Rate")
ax3.set_xticks(range(len(present_cols)))
ax3.set_xticklabels(present_cols, rotation=30, ha="right")
ax3.set_yticks(range(len(coin_sent.index)))
ax3.set_yticklabels(coin_sent.index)
for i in range(len(coin_sent.index)):
    for j in range(len(present_cols)):
        val = coin_sent.values[i, j]
        if not np.isnan(val):
            ax3.text(j, i, f"{val:.0%}", ha="center", va="center",
                     fontsize=9, fontweight="bold",
                     color="white" if val < 0.7 else "#0d1117")
ax3.set_title("Win Rate — Coin × Market Sentiment")
plt.tight_layout()
st.pyplot(fig3); plt.close()
 
st.markdown("---")
 
# ── PLOT 2 — Hourly Activity & Win Rate ────────────────────────────────────────
st.subheader("Plot 4 · Hourly Trade Activity & Win Rate")
st.caption("When do traders trade most — and when do they win most?")
 
hourly = df_f.groupby("hour").agg(
    trade_count=("is_win","count"),
    win_rate=("is_win","mean")
).reset_index()
 
fig4, ax4a = plt.subplots(figsize=(12, 4))
ax4b = ax4a.twinx()
ax4a.bar(hourly["hour"], hourly["trade_count"],
         color=PURPLE, alpha=0.6, label="Trade Count", zorder=2)
ax4b.plot(hourly["hour"], hourly["win_rate"]*100,
          color=GOLD, linewidth=2.2, marker="o", markersize=4,
          label="Win Rate %", zorder=3)
ax4b.axhline(50, color="#30363d", linewidth=0.8, linestyle="--")
ax4a.set_xlabel("Hour of Day (IST)")
ax4a.set_ylabel("Trade Count", color=PURPLE)
ax4b.set_ylabel("Win Rate (%)", color=GOLD)
ax4a.set_xticks(range(24))
ax4a.set_title("Hourly Trade Activity & Win Rate")
ax4a.grid(True, axis="y", zorder=0)
l1, lb1 = ax4a.get_legend_handles_labels()
l2, lb2 = ax4b.get_legend_handles_labels()
ax4a.legend(l1+l2, lb1+lb2, fontsize=8, loc="upper right")
plt.tight_layout()
st.pyplot(fig4); plt.close()
 
st.markdown("---")
 
# ── PLOT 3 — Monthly Volume vs PnL ────────────────────────────────────────────
st.subheader("Plot 7 · Monthly Trade Volume vs Net PnL")
st.caption("Do high-volume months actually make money?")
 
monthly = df_f.groupby("month").agg(
    trade_count=("net_pnl","count"),
    total_pnl=("net_pnl","sum")
).reset_index()
 
fig7, ax7a = plt.subplots(figsize=(12, 4))
ax7b = ax7a.twinx()
ax7a.bar(monthly["month"], monthly["trade_count"],
         color=PURPLE, alpha=0.55, width=20, label="Trade Volume", zorder=2)
ax7b.plot(monthly["month"], monthly["total_pnl"],
          color=GOLD, linewidth=2.2, marker="o", markersize=5,
          label="Monthly PnL ($)", zorder=3)
ax7b.fill_between(monthly["month"], monthly["total_pnl"], 0,
                  where=monthly["total_pnl"]>=0, alpha=0.12, color=GREEN)
ax7b.fill_between(monthly["month"], monthly["total_pnl"], 0,
                  where=monthly["total_pnl"]<0, alpha=0.12, color=RED)
ax7b.axhline(0, color="#30363d", linewidth=0.8, linestyle="--")
ax7a.set_xlabel("Month")
ax7a.set_ylabel("Trade Volume", color=PURPLE)
ax7b.set_ylabel("Net PnL (USD)", color=GOLD)
ax7a.set_title("Monthly Trade Volume vs Net PnL")
plt.xticks(rotation=30, ha="right")
ax7a.grid(True, axis="y", zorder=0)
l1, lb1 = ax7a.get_legend_handles_labels()
l2, lb2 = ax7b.get_legend_handles_labels()
ax7a.legend(l1+l2, lb1+lb2, fontsize=8, loc="upper left")
plt.tight_layout()
st.pyplot(fig7); plt.close()
 
st.markdown("---")
 
# ── PLOT 4 — Coin PnL: Long vs Short ──────────────────────────────────────────
st.subheader("Plot 9 · Avg PnL per Coin — Long vs Short")
st.caption("Which coins are best longed? Which are best shorted?")
 
coin_dir = (
    df_f[df_f["Coin"].isin(sel_coins)]
    .groupby(["Coin","is_long"])["net_pnl"]
    .mean().unstack()
)
coin_dir.columns = ["Short","Long"]
coin_dir = coin_dir.sort_values("Long", ascending=True)
 
fig9, ax9 = plt.subplots(figsize=(10, 5))
x = range(len(coin_dir)); w = 0.35
ax9.barh([i-w/2 for i in x], coin_dir["Long"].values,
         height=w, color=GREEN, alpha=0.8, label="Long", zorder=3)
ax9.barh([i+w/2 for i in x], coin_dir["Short"].values,
         height=w, color=RED,   alpha=0.8, label="Short", zorder=3)
ax9.set_yticks(list(x)); ax9.set_yticklabels(coin_dir.index)
ax9.axvline(0, color="#30363d", linewidth=0.8)
ax9.set_xlabel("Average Net PnL (USD)")
ax9.set_title("Avg PnL per Coin — Long vs Short")
ax9.legend(); ax9.grid(True, axis="x", zorder=0)
plt.tight_layout()
st.pyplot(fig9); plt.close()
 
st.markdown("---")
 
#SImple Prediction Model on next-day trader profitability bucket or volatility of PnL using sentiment + behavior features
st.header("Predict Next-Day Trader Profitability")
st.caption("Random Forest trained on sentiment + behavior features → predicts PnL bucket")
 
# ── daily feature table ─────────────────────────────────────────────────
@st.cache_data
def build_features(data):
    daily = data.groupby(["Account","date"]).agg(
        sentiment    = ("classification", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "Neutral"),
        win_rate     = ("is_win",         "mean"),
        avg_size     = ("Size USD",       "mean"),
        aggression   = ("Crossed",        "mean"),
        long_rate    = ("is_long",        "mean"),
        trade_count  = ("net_pnl",        "count"),
        avg_drawdown = ("drawdown",       "mean"),
        daily_pnl    = ("net_pnl",        "sum"),
    ).reset_index().sort_values(["Account","date"])
 
    # next-day PnL target
    daily["next_pnl"] = daily.groupby("Account")["daily_pnl"].shift(-1)
    daily.dropna(subset=["next_pnl"], inplace=True)
 
    # bucket: Loss / Small Gain / Big Gain
    daily["pnl_bucket"] = pd.cut(
        daily["next_pnl"],
        bins=[-np.inf, 0, 500, np.inf],
        labels=["Loss", "Small Gain", "Big Gain"]
    )
 
    le = LabelEncoder()
    daily["sent_enc"] = le.fit_transform(daily["sentiment"])
    return daily, le
 
feat_df, le = build_features(df)
 
FEATURES = ["sent_enc","win_rate","avg_size","aggression",
            "long_rate","trade_count","avg_drawdown"]
X = feat_df[FEATURES]
y = feat_df["pnl_bucket"]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
 
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
acc    = (y_pred == y_test).mean()
 
# ── Model metrics ─────────────────────────────────────────────────────────────
col_m1, col_m2 = st.columns([1, 2])
 
with col_m1:
    st.metric("Model Accuracy", f"{acc*100:.1f}%")
    st.markdown("**Target classes**")
    st.markdown("- 🔴 Loss (next-day PnL < 0)")
    st.markdown("- 🟡 Small Gain (0 – $500)")
    st.markdown("- 🟢 Big Gain  (> $500)")
 
with col_m2:
    report = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).T.round(2)
    st.dataframe(report_df.style.background_gradient(cmap="RdYlGn", axis=None),
                 use_container_width=True)
 
# ── Feature importance chart ──────────────────────────────────────────────────
st.subheader("Feature Importances")
imp = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
 
fig_imp, ax_imp = plt.subplots(figsize=(8, 3))
colors_imp = [GREEN if v == imp.max() else PURPLE for v in imp.values]
ax_imp.barh(imp.index, imp.values, color=colors_imp, alpha=0.85)
ax_imp.set_title("What drives next-day profitability?")
ax_imp.set_xlabel("Importance")
ax_imp.grid(True, axis="x")
plt.tight_layout()
st.pyplot(fig_imp); plt.close()
 
# ── Live predictor ────────────────────────────────────────────────────────────
st.subheader("Try it — Predict for a Custom Scenario")
with st.form("predict_form"):
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        p_sent       = st.selectbox("Sentiment", SENT_ORDER)
        p_win_rate   = st.slider("Win Rate", 0.0, 1.0, 0.6, 0.05)
        p_long_rate  = st.slider("Long Rate", 0.0, 1.0, 0.5, 0.05)
    with pc2:
        p_avg_size   = st.number_input("Avg Trade Size ($)", 100, 500000, 2000, 500)
        p_aggression = st.slider("Cross-Margin Rate", 0.0, 1.0, 0.4, 0.05)
    with pc3:
        p_trades     = st.slider("Trades Today", 1, 50, 10)
        p_drawdown   = st.number_input("Avg Drawdown ($)", 0, 100000, 500, 100)
    submitted = st.form_submit_button("Predict Next-Day Bucket")
 
if submitted:
    sent_enc_val = le.transform([p_sent])[0]
    row = pd.DataFrame([[sent_enc_val, p_win_rate, p_avg_size, p_aggression,
                         p_long_rate, p_trades, p_drawdown]],
                       columns=FEATURES)
    pred      = model.predict(row)[0]
    proba     = model.predict_proba(row)[0]
    class_map = {c: p for c, p in zip(model.classes_, proba)}
 
    color_map = {"Loss": "🔴", "Small Gain": "🟡", "Big Gain": "🟢"}
    st.success(f"**Predicted bucket: {color_map[pred]} {pred}**")
 
    prob_df = pd.DataFrame({
        "Bucket": list(class_map.keys()),
        "Probability": [f"{v*100:.1f}%" for v in class_map.values()]
    })
    st.table(prob_df)
 
st.markdown("---")
 
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CLUSTERING / BEHAVIORAL ARCHETYPES
# ═══════════════════════════════════════════════════════════════════════════════
st.header("Trader Behavioral Archetypes (K-Means Clustering)")
st.caption(f"Grouping 32 accounts into {n_clusters} archetypes based on trading behavior")
 
# ── trader-level feature matrix ─────────────────────────────────────────
@st.cache_data
def build_trader_features(data):
    tdf = data.groupby("Account").agg(
        avg_pnl      = ("net_pnl",        "mean"),
        pnl_std      = ("net_pnl",        "std"),
        win_rate     = ("is_win",         "mean"),
        avg_size     = ("Size USD",       "mean"),
        aggression   = ("Crossed",        "mean"),
        long_rate    = ("is_long",        "mean"),
        max_drawdown = ("drawdown",       "max"),
        total_trades = ("net_pnl",        "count"),
    ).reset_index().fillna(0)
    return tdf
 
trader_feats = build_trader_features(df)
CLUSTER_COLS = ["avg_pnl","pnl_std","win_rate","avg_size",
                "aggression","long_rate","max_drawdown","total_trades"]
 
scaler  = StandardScaler()
X_clust = scaler.fit_transform(trader_feats[CLUSTER_COLS])
 
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
trader_feats["cluster"] = kmeans.fit_predict(X_clust)
 
# ── Cluster summary table ─────────────────────────────────────────────────────
clust_summary = trader_feats.groupby("cluster")[CLUSTER_COLS].mean().round(2)
clust_summary.index = [f"Archetype {i}" for i in clust_summary.index]
st.dataframe(clust_summary.style.background_gradient(cmap="RdYlGn"),
             use_container_width=True)
 
# ── Cluster bar charts ────────────────────────────────────────────────────────
clust_plot_cols = ["avg_pnl","win_rate","avg_size","aggression","max_drawdown"]
clust_labels    = ["Avg PnL ($)","Win Rate","Avg Size ($)","Aggression","Max Drawdown ($)"]
clust_colors    = [GREEN, GREED, FEAR, GOLD, PURPLE, RED]
 
fig_cl, axes_cl = plt.subplots(1, len(clust_plot_cols),
                                figsize=(16, 4))
fig_cl.suptitle("Behavioral Archetype Comparison", fontsize=13)
 
for ax, col, lbl in zip(axes_cl, clust_plot_cols, clust_labels):
    vals  = clust_summary[col].values
    names = clust_summary.index.tolist()
    bars  = ax.bar(names, vals,
                   color=clust_colors[:n_clusters],
                   edgecolor="none", zorder=3)
    ax.bar_label(bars, fmt="%.1f", padding=3,
                 color="#e6edf3", fontsize=7, fontweight="bold")
    ax.set_title(lbl, fontsize=9)
    ax.set_xticklabels(names, rotation=25, ha="right", fontsize=7)
    ax.grid(True, axis="y", zorder=0)
 
plt.tight_layout()
st.pyplot(fig_cl); plt.close()
 
# ── Scatter: win rate vs avg pnl coloured by cluster ──────────────────────────
st.subheader("Archetype Map — Win Rate vs Avg PnL")
fig_sc, ax_sc = plt.subplots(figsize=(8, 5))
 
for c in range(n_clusters):
    sub = trader_feats[trader_feats["cluster"]==c]
    ax_sc.scatter(sub["win_rate"]*100, sub["avg_pnl"],
                  color=clust_colors[c], s=80, alpha=0.85,
                  label=f"Archetype {c}", zorder=3)
    for _, row in sub.iterrows():
        ax_sc.annotate(row["Account"][:8]+"…",
                       (row["win_rate"]*100, row["avg_pnl"]),
                       fontsize=6, color="#8b949e",
                       xytext=(4,4), textcoords="offset points")
 
ax_sc.axhline(0, color="#30363d", linewidth=0.8, linestyle="--")
ax_sc.axvline(50, color="#30363d", linewidth=0.8, linestyle="--")
ax_sc.set_xlabel("Win Rate (%)"); ax_sc.set_ylabel("Avg PnL (USD)")
ax_sc.set_title("Trader Archetypes — Win Rate vs Avg PnL")
ax_sc.legend(fontsize=9); ax_sc.grid(True)
plt.tight_layout()
st.pyplot(fig_sc); plt.close()
 
# ── Per-account cluster assignment ────────────────────────────────────────────
st.subheader("Account → Archetype Assignment")
display_df = trader_feats[["Account","cluster","avg_pnl","win_rate",
                             "aggression","max_drawdown","total_trades"]].copy()
display_df["win_rate"]   = (display_df["win_rate"]*100).round(1).astype(str)+"%"
display_df["avg_pnl"]    = display_df["avg_pnl"].round(1)
display_df["aggression"] = display_df["aggression"].round(3)
display_df["cluster"]    = display_df["cluster"].apply(lambda x: f"Archetype {x}")
display_df.columns       = ["Account","Archetype","Avg PnL","Win Rate",
                              "Aggression","Max Drawdown","Total Trades"]
st.dataframe(display_df.set_index("Account"), use_container_width=True)
 
st.markdown("---")