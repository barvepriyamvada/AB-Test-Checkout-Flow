import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import norm, mannwhitneyu
from scipy.stats import chi2_contingency
import warnings
warnings.filterwarnings('ignore')

# ── Color palette ──────────────────────────────────────────────
PRIMARY_BLUE  = '#1B4F72'
ORANGE        = '#E67E22'
LIGHT_BLUE    = '#AED6F1'
LIGHT_ORANGE  = '#FAD7A0'
GREEN         = '#1E8449'
RED           = '#C0392B'
YELLOW        = '#D4AC0D'

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title='A/B Test Analyzer — Checkout Flow',
    page_icon='🛒',
    layout='wide',
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.metric-label { font-size: 14px; font-weight: 600; color: #555; margin-bottom: 6px; }
.metric-value { font-size: 38px; font-weight: 800; line-height: 1; }
.metric-sub   { font-size: 13px; color: #777; margin-top: 6px; }
.stat-box {
    background: #F4F6F7;
    border-radius: 10px;
    padding: 18px 24px;
    margin-top: 12px;
}
.verdict-box {
    border-radius: 12px;
    padding: 20px 28px;
    margin-top: 12px;
    text-align: center;
}
.section-header {
    font-size: 20px;
    font-weight: 700;
    color: #1B4F72;
    border-bottom: 2px solid #AED6F1;
    padding-bottom: 6px;
    margin: 24px 0 16px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────
st.title('A/B Test Analyzer — Checkout Flow Optimizer')
st.markdown('**Upload your test results and get an instant go/no-go recommendation.**')
st.markdown('---')

# ══════════════════════════════════════════════════════════════
# SIDEBAR — Upload & Configure
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('## Upload & Configure')

    uploaded = st.file_uploader('Upload A/B test CSV', type=['csv'])

    use_sample = st.checkbox('Use sample dataset (checkout_ab_test.csv)', value=(uploaded is None))

    if uploaded:
        df = pd.read_csv(uploaded)
    elif use_sample:
        try:
            df = pd.read_csv('data/raw/checkout_ab_test.csv')
            st.success(f'Sample data loaded: {len(df):,} rows')
        except FileNotFoundError:
            st.error('Sample file not found. Please upload a CSV.')
            st.stop()
    else:
        st.info('Please upload a CSV or check "Use sample dataset".')
        st.stop()

    st.markdown('---')
    st.markdown('### Column Mapping')
    all_cols = df.columns.tolist()

    group_col = st.selectbox('Group column', all_cols,
                              index=all_cols.index('group') if 'group' in all_cols else 0)

    outcome_col = st.selectbox('Outcome column (binary 0/1)', all_cols,
                                index=all_cols.index('completed_checkout')
                                if 'completed_checkout' in all_cols else 0)

    groups = df[group_col].unique().tolist()
    control_val   = st.selectbox('Control group label',   groups,
                                  index=groups.index('control') if 'control' in groups else 0)
    treatment_val = st.selectbox('Treatment group label', groups,
                                  index=groups.index('treatment') if 'treatment' in groups else
                                  (1 if len(groups) > 1 else 0))

    st.markdown('---')
    st.markdown('### Test Parameters')
    alpha = st.slider('Significance level (α)', 0.01, 0.10, 0.05, 0.01,
                       help='Probability threshold for statistical significance.')

    st.markdown('---')
    st.markdown('### Business Assumptions')
    monthly_visitors   = st.number_input('Monthly visitors',       value=500000,  step=10000)
    avg_order_value    = st.number_input('Average order value ($)', value=85.0,    step=5.0)
    implementation_cost= st.number_input('Implementation cost ($)', value=25000,   step=1000)

# ══════════════════════════════════════════════════════════════
# DATA PREP
# ══════════════════════════════════════════════════════════════
ctrl_df = df[df[group_col] == control_val]
trt_df  = df[df[group_col] == treatment_val]

n_ctrl  = len(ctrl_df)
n_trt   = len(trt_df)
x_ctrl  = ctrl_df[outcome_col].sum()
x_trt   = trt_df[outcome_col].sum()
p_ctrl  = x_ctrl / n_ctrl
p_trt   = x_trt  / n_trt
diff    = p_trt - p_ctrl
lift_pct= diff / p_ctrl * 100

# Z-test
p_pool  = (x_ctrl + x_trt) / (n_ctrl + n_trt)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/n_ctrl + 1/n_trt))
z_stat  = (p_trt - p_ctrl) / se_pool
p_value = 1 - norm.cdf(z_stat)   # one-tailed

# 95% CI
se_diff  = np.sqrt((p_ctrl*(1-p_ctrl)/n_ctrl) + (p_trt*(1-p_trt)/n_trt))
z_95     = norm.ppf(0.975)
ci_lower = diff - z_95 * se_diff
ci_upper = diff + z_95 * se_diff

# Chi-square
contingency = np.array([[x_ctrl, n_ctrl - x_ctrl],
                          [x_trt,  n_trt  - x_trt]])
chi2_val, p_chi2, _, _ = chi2_contingency(contingency)

# ══════════════════════════════════════════════════════════════
# SECTION 2 — Results
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)

# Row 1 — Metric cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="background:#EAECEE;">
        <div class="metric-label">Control Rate</div>
        <div class="metric-value" style="color:#555;">{p_ctrl*100:.1f}%</div>
        <div class="metric-sub">{x_ctrl:,} / {n_ctrl:,} completed</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background:#D6EAF8;">
        <div class="metric-label">Treatment Rate</div>
        <div class="metric-value" style="color:{PRIMARY_BLUE};">{p_trt*100:.1f}%</div>
        <div class="metric-sub">{x_trt:,} / {n_trt:,} completed</div>
    </div>""", unsafe_allow_html=True)

with col3:
    lift_color = GREEN if lift_pct > 0 else RED
    lift_sign  = '+' if lift_pct > 0 else ''
    st.markdown(f"""
    <div class="metric-card" style="background:#D5F5E3;">
        <div class="metric-label">Lift</div>
        <div class="metric-value" style="color:{lift_color};">{lift_sign}{lift_pct:.1f}%</div>
        <div class="metric-sub">{lift_sign}{diff*100:.2f} percentage points</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# Row 2 — Bar chart
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar([f'Control\n({control_val})', f'Treatment\n({treatment_val})'],
              [p_ctrl*100, p_trt*100],
              color=[PRIMARY_BLUE, ORANGE], width=0.45, edgecolor='white')

for bar, val in zip(bars, [p_ctrl*100, p_trt*100]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')

ax.set_ylim(0, max(p_ctrl*100, p_trt*100) * 1.3)
ax.set_ylabel('Completion Rate (%)', fontsize=11)
ax.set_title('Checkout Completion Rate: Control vs Treatment', fontsize=12, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# Row 3 — Statistical Results
st.markdown('<div class="section-header">Statistical Results</div>', unsafe_allow_html=True)

p_color   = 'green' if p_value < alpha else 'red'
p_label   = 'SIGNIFICANT' if p_value < alpha else 'NOT SIGNIFICANT'

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""
    <div class="stat-box">
        <b>Test used:</b> Z-test for proportions (one-tailed) + Chi-square<br><br>
        <b>p-value:</b> <span style="color:{p_color}; font-weight:bold; font-size:18px;">
            {p_value:.6f}</span>
        &nbsp; → &nbsp; <span style="color:{p_color}; font-weight:bold;">{p_label}</span><br><br>
        <b>Chi-square statistic:</b> {chi2_val:.4f} &nbsp;|&nbsp; p = {p_chi2:.6f}<br>
        <b>Z-statistic:</b> {z_stat:.4f}
    </div>""", unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="stat-box">
        <b>95% Confidence Interval:</b><br>
        <span style="font-size:16px; font-weight:bold;">
            [{ci_lower*100:.2f}pp, {ci_upper*100:.2f}pp]</span><br><br>
        <b>Sample sizes:</b><br>
        Control: {n_ctrl:,} &nbsp;|&nbsp; Treatment: {n_trt:,}<br><br>
        <b>Significance level (α):</b> {alpha}
    </div>""", unsafe_allow_html=True)

# Row 4 — Traffic light verdict
st.markdown('<div class="section-header">Verdict</div>', unsafe_allow_html=True)

if p_value < alpha and diff > 0:
    verdict_color = '#1E8449'
    verdict_bg    = '#D5F5E3'
    verdict_icon  = '🟢'
    verdict_text  = 'STATISTICALLY SIGNIFICANT — Deploy'
    verdict_sub   = f'The single-page checkout improves completion rate by {diff*100:.2f}pp. Safe to deploy.'
elif p_value >= alpha and p_value < alpha * 2:
    verdict_color = '#D4AC0D'
    verdict_bg    = '#FEF9E7'
    verdict_icon  = '🟡'
    verdict_text  = 'BORDERLINE — Collect More Data'
    verdict_sub   = 'Result is close to significance. Run the test for longer to increase confidence.'
else:
    verdict_color = '#C0392B'
    verdict_bg    = '#FADBD8'
    verdict_icon  = '🔴'
    verdict_text  = 'NOT SIGNIFICANT — Do Not Deploy'
    verdict_sub   = 'The observed difference could be due to chance. Do not deploy based on this result.'

st.markdown(f"""
<div class="verdict-box" style="background:{verdict_bg}; border: 2px solid {verdict_color};">
    <div style="font-size:32px;">{verdict_icon}</div>
    <div style="font-size:22px; font-weight:800; color:{verdict_color}; margin:8px 0;">{verdict_text}</div>
    <div style="font-size:14px; color:#444;">{verdict_sub}</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 3 — Business Impact
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Business Impact</div>', unsafe_allow_html=True)

current_completions    = monthly_visitors * p_ctrl
treatment_completions  = monthly_visitors * p_trt
additional_monthly     = treatment_completions - current_completions
additional_monthly_rev = additional_monthly * avg_order_value
additional_annual_rev  = additional_monthly_rev * 12
payback_months         = implementation_cost / additional_monthly_rev if additional_monthly_rev > 0 else float('inf')
three_year_return      = additional_annual_rev * 3
three_year_roi         = (three_year_return - implementation_cost) / implementation_cost * 100 if implementation_cost > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Additional completions/mo', f'+{additional_monthly:,.0f}')
with col2:
    st.metric('Additional revenue/mo', f'+${additional_monthly_rev:,.0f}')
with col3:
    st.metric('Annual revenue uplift', f'+${additional_annual_rev:,.0f}')
with col4:
    pb_str = f'{payback_months:.1f} months' if payback_months != float('inf') else 'N/A'
    st.metric('Payback period', pb_str)

st.markdown('<br>', unsafe_allow_html=True)

# ROI bar chart
fig2, ax2 = plt.subplots(figsize=(8, 4))
categories = ['Implementation\nCost', 'Month 1\nRevenue', '12-Month\nRevenue', '3-Year\nRevenue']
values     = [implementation_cost, additional_monthly_rev, additional_annual_rev, three_year_return]
colors_roi = [RED, LIGHT_ORANGE, ORANGE, PRIMARY_BLUE]

bars2 = ax2.bar(categories, values, color=colors_roi, edgecolor='white', width=0.5)
for bar, val in zip(bars2, values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
             f'${val:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_ylabel('USD ($)', fontsize=11)
ax2.set_title(f'Cost vs. Revenue Impact  |  3-Year ROI: {three_year_roi:,.0f}%',
              fontsize=12, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
st.pyplot(fig2)
plt.close()

# Summary table
impact_df = pd.DataFrame({
    'Metric': [
        'Current monthly completions', 'Projected monthly completions',
        'Additional completions/month', 'Additional revenue/month',
        'Additional revenue/year', 'Implementation cost',
        'Payback period', '3-Year incremental revenue', '3-Year ROI'
    ],
    'Value': [
        f'{current_completions:,.0f}', f'{treatment_completions:,.0f}',
        f'+{additional_monthly:,.0f}', f'+${additional_monthly_rev:,.0f}',
        f'+${additional_annual_rev:,.0f}', f'${implementation_cost:,.0f}',
        pb_str, f'${three_year_return:,.0f}', f'{three_year_roi:,.0f}%'
    ]
})
st.dataframe(impact_df, use_container_width=True, hide_index=True)

st.markdown('---')
st.caption('A/B Test Analyzer | Portfolio Project 4 — Priyamvada Barve')
