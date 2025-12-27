# 原始連結（不知何時失效）
# https://app.snowflake.com/sfedu02/nnb82355/#/streamlit-apps/SNOWBEARAIR_DB.PUBLIC.QGYT2I_2ZGCO45N3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="LA Permit Analysis",
    page_icon="🏗️",
    layout="wide"
)

# --- CSS 美化 (升級版) ---
st.markdown("""
<style>
    /* 全局字體與背景微調 */
    .block-container { 
        padding-top: 2rem; 
        padding-bottom: 5rem;
    }
    
    /* 控制面板卡片化 - 增加陰影與圓角 */
    .control-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        border-left: 5px solid #4ECDC4; /* 裝飾線條 */
    }
    
    /* 標題樣式 */
    .chart-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 15px;
        border-left: 4px solid #FF6B6B;
        padding-left: 10px;
        background: linear-gradient(90deg, #fdfbfb 0%, #ebedee 100%);
        padding: 10px;
        border-radius: 0 10px 10px 0;
    }

    /* KPI 指標卡優化 */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 資料讀取 (保持原有的極致防呆邏輯) ---
@st.cache_data
def load_data_final():
    session = get_active_session()
    try:
        records_df = session.table("LA_PERMIT_DATA.PUBLIC.PERMIT_RECORDS").to_pandas()
        census_df = session.table("LA_PERMIT_DATA.PUBLIC.CENSUS_TRACTS").to_pandas()

        records_df.columns = [c.upper() for c in records_df.columns]
        census_df.columns = [c.upper() for c in census_df.columns]

        # Date
        date_col = None
        possible_dates = [c for c in records_df.columns if 'DATE' in c]
        if possible_dates:
            preferred = [c for c in possible_dates if 'ISSUE' in c]
            date_col = preferred[0] if preferred else possible_dates[0]
            records_df[date_col] = pd.to_datetime(records_df[date_col], errors="coerce")

        # Valuation
        val_col = 'VALUATION'
        if val_col not in records_df.columns:
            records_df[val_col] = 0.0
        else:
            records_df[val_col] = (
                records_df[val_col].astype(str).str.replace(r"[$,]", "", regex=True)
            )
            records_df[val_col] = pd.to_numeric(records_df[val_col], errors="coerce").fillna(0.0)

        # Merge logic
        if "CENSUS_TRACT" not in records_df.columns:
            return None, None, None, "Missing CENSUS_TRACT Column"

        records_df['CT_Num'] = pd.to_numeric(records_df['CENSUS_TRACT'], errors='coerce').fillna(0)
        records_df['CT_To_Combine'] = records_df['CT_Num'] * 100 + 6037000000

        merged_df = records_df.merge(
            census_df,
            left_on="CT_To_Combine",
            right_on="CENSUS_TRACT",
            how="inner"
        )

        return merged_df, date_col, val_col, None

    except Exception as e:
        return None, None, None, str(e)

with st.spinner("Fetching Data..."):
    df, date_col, val_col, err = load_data_final()

if err:
    st.error(f"❌ Critical Error: {err}")
    st.stop()


# --- 3. 控制面板 UI (美化版) ---

st.title("🏗️ LA Permit Analysis Dashboard")
st.markdown("""
<div style='background-color: #e8f4f8; padding: 15px; border-radius: 10px; border-left: 5px solid #3498db; margin-bottom: 20px;'>
    <strong>Note:</strong> This dashboard compares construction priorities between 
    <span style='color:#FF6B6B; font-weight:bold;'>Low Income</span> and 
    <span style='color:#4ECDC4; font-weight:bold;'>High Income</span> neighborhoods in Los Angeles.
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Settings & Filters")
    st.markdown("---") # 分隔線

    col1, col2, col3 = st.columns(3)

    all_ami = sorted(df['AMI_CATEGORY'].astype(str).unique())
    all_types = sorted(df['PERMIT_TYPE'].astype(str).unique())

    def_low = [x for x in all_ami if 'Low' in x]
    def_high = [x for x in all_ami if 'Above Moderate' in x]

    default_ess = ['Bldg-Alter/Repair','Electrical','Plumbing','Bldg-Demolition','Fire Sprinkler','HVAC']
    default_ess = [x for x in default_ess if x in all_types]

    with col1:
        st.markdown("**1. Income Groups**")
        g_low = st.multiselect("🔴 Low Income", all_ami, default=def_low)
        g_high = st.multiselect("🔵 High Income", all_ami, default=def_high)

    with col2:
        st.markdown("**2. Analysis Parameters**")
        sel_ess = st.multiselect("🛠️ Essential Types", all_types, default=default_ess)

    with col3:
        st.markdown("**3. Cost Filter**")
        max_val = df[val_col].max()
        if max_val > 1000:
            val_limit = st.number_input("💰 Max Project Cost ($)",
                min_value=0.0,
                max_value=float(max_val),
                value=float(max_val)
            )
        else:
            st.info("⚠️ No valuation data, using full dataset.")
            val_limit = 1e20

    st.markdown('</div>', unsafe_allow_html=True)


# --- 4. 過濾資料 ---

mask = df[val_col] <= val_limit
filtered = df[mask]

df_low = filtered[filtered['AMI_CATEGORY'].isin(g_low)]
df_high = filtered[filtered['AMI_CATEGORY'].isin(g_high)]

if df_low.empty or df_high.empty:
    st.warning("⚠️ Filters result in empty dataset. Please adjust your selection.")
    st.stop()

s_low = df_low['PERMIT_TYPE'].value_counts(normalize=True)
s_high = df_high['PERMIT_TYPE'].value_counts(normalize=True)

comp = pd.DataFrame({'Low': s_low, 'High': s_high}).fillna(0)
comp['Diff'] = comp['High'] - comp['Low']


# --- 5. KPI 區塊 ---
# 使用 container 稍微隔離 KPI 區塊
with st.container():
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Low Income Permits", f"{len(df_low):,}", help="Total records matching Low Income criteria")
    k2.metric("High Income Permits", f"{len(df_high):,}", help="Total records matching High Income criteria")

    low_e = s_low[s_low.index.isin(sel_ess)].sum()
    high_e = s_high[s_high.index.isin(sel_ess)].sum()

    k3.metric("Low Income: Essential %", f"{low_e:.1%}", delta="Focus on Basics", delta_color="normal")
    k4.metric("High Income: Essential %", f"{high_e:.1%}", delta=f"{(high_e-low_e)*100:.1f} pts vs Low", delta_color="inverse")


# --- 共用繪圖函式 (確保風格統一) ---
def update_layout_style(fig, height=450):
    fig.update_layout(
        template="plotly_white", # 乾淨的白色背景
        height=height,
        margin=dict(t=30, b=10, l=10, r=10),
        font=dict(family="Verdana, sans-serif", size=12, color="#333"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Verdana")
    )
    return fig

# --- 6. Chart 1: Permit Type Comparison ---

st.markdown('<div class="chart-title">1. Comparison of Permit Types</div>', unsafe_allow_html=True)

top_n = (comp['Low'] + comp['High']).sort_values(ascending=False).head(12).index.tolist()
top_n = [i for i in top_n if i in comp.index]

comp2 = comp.loc[top_n].reset_index()
comp2.rename(columns={comp2.columns[0]: "PermitType"}, inplace=True)

viz1 = comp2.melt(id_vars="PermitType", value_vars=["Low", "High"])

fig1 = px.bar(
    viz1,
    x="PermitType",
    y="value",
    color="variable",
    barmode="group",
    labels={"value": "Proportion", "PermitType": "Permit Type", "variable": "Group"},
    color_discrete_map={"Low": "#FF6B6B", "High": "#4ECDC4"},
)
fig1.update_traces(hovertemplate='%{y:.1%} <br>%{x}')
fig1 = update_layout_style(fig1)
fig1.update_layout(xaxis_tickangle=-45, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig1, use_container_width=True)


# --- 7. Chart 2 & 3: Donut Charts (Interactive) ---

st.markdown('<div class="chart-title">2 & 3. Composition Analysis</div>', unsafe_allow_html=True)

c2, c3 = st.columns(2)

def donut(series, title, palette):
    s = series.copy()
    if len(s) > 6:
        s = s.sort_values(ascending=False)
        s = pd.concat([s.head(6), pd.Series({'Others': s.iloc[6:].sum()})])

    fig = go.Figure(go.Pie(
        labels=s.index,
        values=s.values,
        hole=0.5, # 甜甜圈孔徑
        marker=dict(colors=palette),
        textinfo='percent+label', # 直接顯示百分比與標籤
        textposition='inside',
        insidetextorientation='radial'
    ))
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        showlegend=False # 隱藏圖例，讓畫面更乾淨
    )
    return update_layout_style(fig, height=400)

with c2:
    st.plotly_chart(donut(s_low, "Low Income Composition", px.colors.sequential.Reds_r), use_container_width=True)

with c3:
    st.plotly_chart(donut(s_high, "High Income Composition", px.colors.sequential.Tealgrn_r), use_container_width=True)


# --- 8. Chart 4: Cumulative Curve (Visual Upgrade) ---

st.markdown('<div class="chart-title">4. Cumulative Share (Essentials First)</div>', unsafe_allow_html=True)
st.caption("Ordering: Essential categories (left) to Non-essential (right). Steeper initial slope = higher reliance on basic repairs.")

e_idx = [x for x in comp.index if x in sel_ess]
o_idx = [x for x in comp.index if x not in sel_ess]

e_idx = comp.loc[e_idx].sum(axis=1).sort_values(ascending=False).index.tolist()
o_idx = comp.loc[o_idx].sum(axis=1).sort_values(ascending=False).index.tolist()

order = e_idx + o_idx
ordered = comp.loc[order].copy()
ordered['LowCum'] = ordered['Low'].cumsum()
ordered['HighCum'] = ordered['High'].cumsum()

fig4 = go.Figure()
# 使用 fill='tozeroy' 增加區域填滿效果，視覺更強烈
fig4.add_trace(go.Scatter(
    x=ordered.index, y=ordered['LowCum'], 
    name="Low Income", mode='lines', 
    line=dict(color="#FF6B6B", width=3),
    fill='tozeroy', fillcolor='rgba(255, 107, 107, 0.1)' # 半透明紅色填滿
))
fig4.add_trace(go.Scatter(
    x=ordered.index, y=ordered['HighCum'], 
    name="High Income", mode='lines', 
    line=dict(color="#4ECDC4", width=3, dash='dot'),
    # High income 不填滿，避免顏色混雜，或是用極淡的顏色
))

if len(e_idx) > 0:
    fig4.add_vline(x=len(e_idx)-0.5, line_dash="dash", line_color="#888", annotation_text="End of Essentials", annotation_position="top right")

fig4 = update_layout_style(fig4, height=500)
fig4.update_layout(xaxis_tickangle=-45, yaxis_title="Cumulative Share", legend=dict(x=0.01, y=0.99))
st.plotly_chart(fig4, use_container_width=True)


# --- 9. Chart 5: Difference (Zero-Line & Aesthetics) ---

st.markdown('<div cl ss="chart-title">5. Preference Gap (High - Low)</div>', unsafe_allow_html=True)
st.caption("Right (Teal) = Preferred by High Income. Left (Red) = Preferred by Low Income.")

diff_df = comp[abs(comp["Diff"]) > 0.002].sort_values("Diff")
diff_df["Color"] = diff_df["Diff"].apply(lambda x: "#4ECDC4" if x > 0 else "#FF6B6B")

fig5 = go.Figure(go.Bar(
    x=diff_df["Diff"],
    y=diff_df.index,
    orientation="h",
    marker_color=diff_df["Color"],
    text=diff_df["Diff"].apply(lambda x: f"{x:+.1%}"), # 顯示數值
    textposition='auto'
))

# 增加一條明顯的 0 軸線
fig5.add_vline(x=0, line_width=2, line_color="#333")

fig5 = update_layout_style(fig5, height=600)
fig5.update_layout(xaxis_title="Difference (High Share - Low Share)", xaxis_tickformat=".1%")
st.plotly_chart(fig5, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Dashboard powered by Snowflake & Streamlit ❄️</div>", unsafe_allow_html=True)