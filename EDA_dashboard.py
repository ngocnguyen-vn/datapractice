import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------
# CONFIG - UPDATED COLORS
# ------------------------------
st.set_page_config(page_title="Urban Blowout Chic Dashboard", layout="wide")

COLOR_1 = '#5E548E'  # Midnight Purple (Chính)
COLOR_2 = '#BE95C4'  # Soft Lavender (Phụ)
COLOR_3 = '#9F86C0'  # Neutral Purple (Trung tính)
BG_COLOR = '#F7F7FF' # Ice White / Blue tint (Nền)
TEXT_COLOR = '#4A4E69'
DARK_TEXT = '#231942'

# ------------------------------
# STYLE
# ------------------------------
st.markdown(f"""
<style>
.stApp {{ background-color: {BG_COLOR}; }}
.block-container {{ padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }}
header {{ visibility: hidden; }}
.stPlotlyChart {{ background-color: transparent; border-radius: 10px; }}
h1, h2, h3, p {{ color: {TEXT_COLOR} !important; }}
div[data-testid="stMetric"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# CHART STYLE
# ------------------------------
def apply_chart_style(fig, height=210):
    fig.update_layout(
        font=dict(color=DARK_TEXT, size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        hovermode='x unified',
        height=height,
        margin=dict(l=4, r=5, t=20, b=5),
    )
    fig.update_xaxes(
        title_font=dict(color=COLOR_1, size=12),
        tickfont=dict(color=DARK_TEXT, size=10),
        showgrid=True, gridwidth=0.5,
        gridcolor='rgba(94, 84, 142, 0.1)', # Mờ hơn để hợp với tông tím
        showline=True, linecolor='rgba(94, 84, 142, 0.2)'
    )
    fig.update_yaxes(
        title_font=dict(color=COLOR_1, size=12),
        tickfont=dict(color=DARK_TEXT, size=10),
        showgrid=True, gridwidth=0.5,
        gridcolor='rgba(94, 84, 142, 0.1)',
        showline=True, linecolor='rgba(94, 84, 142, 0.2)'
    )
    return fig

def insight_box(text, kind='info'):
    colors = {
        'info':    ('#E0E1DD', COLOR_1,  '#231942'),
        'error':   ('#FDECEF', COLOR_1,  '#78290F'),
        'success': ('#EAF4F4', COLOR_1, '#1B4332'),
    }
    bg, border, txt = colors.get(kind, colors['info'])
    st.markdown(f"""
    <div style="background:{bg}; border-left:3px solid {border};
        border-radius:5px; padding:5px 10px; margin-top:3px;">
        <p style="color:{txt} !important; font-size:0.72rem; margin:0; line-height:1.4;">{text}</p>
    </div>""", unsafe_allow_html=True)

def section_title(text):
    st.markdown(f"""
    <p style="
        color:{COLOR_1} !important;
        font-size:0.85rem;
        font-weight:700;
        letter-spacing:0.06em;
        margin:4px 0 3px 0;
        text-align:center;
        border-bottom:1px solid rgba(94,84,142,0.2);
        padding-bottom:3px;">
        {text}
    </p>
    """, unsafe_allow_html=True)

# ------------------------------
# LOAD DATA
# ------------------------------
@st.cache_data
def load_and_process():
    order_items = pd.read_csv('order_items.csv', dtype={'promo_id': str})
    products    = pd.read_csv('products.csv')
    promotions  = pd.read_csv('promotions.csv')
    orders      = pd.read_csv('orders.csv', parse_dates=['order_date'])

    URBAN_IDS = ['PROMO-0005','PROMO-0015','PROMO-0025','PROMO-0035','PROMO-0045']

    df = order_items.merge(
        products[['product_id','price','cogs']],
        on='product_id',
        how='left'
    )

    df = df.merge(
        orders[['order_id','order_date','customer_id']],
        on='order_id',
        how='left'
    )

    df['year']        = df['order_date'].dt.year
    df['has_promo']   = df['promo_id'].notna()
    df['is_urban']    = df['promo_id'].isin(URBAN_IDS)
    df['revenue']     = df['quantity'] * df['unit_price']
    df['cogs_total']  = df['quantity'] * df['cogs']
    df['profit']      = df['revenue'] - df['cogs_total'] - df['discount_amount']
    df['margin']      = df['profit'] / df['revenue'].replace(0, np.nan)
    df['price_ratio'] = df['unit_price'] / df['price']

    return df, promotions, orders, products


# LOAD
df, promotions, orders, products = load_and_process()

def safe_get(df, cond, col):
    vals = df[cond][col].values
    return vals[0] if len(vals) > 0 else 0

# ------------------------------
# TITLE
# ------------------------------
st.markdown("""
<h1 style="
    text-align:center;
    font-size:2.1rem;
    background: linear-gradient(90deg, #5E548E, #BE95C4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
">
PHÂN TÍCH LỢI NHUẬN KHUYẾN MÃI
</h1>
""", unsafe_allow_html=True)

# ------------------------------
# KPI CARDS
# ------------------------------
summary = df.groupby('has_promo').agg({'margin': 'mean', 'profit': 'sum'}).reset_index()

margin_no_promo   = safe_get(summary, summary['has_promo']==False, 'margin')
margin_with_promo = safe_get(summary, summary['has_promo']==True,  'margin')
profit_no_promo   = safe_get(summary, summary['has_promo']==False, 'profit') / 1e9
profit_with_promo = safe_get(summary, summary['has_promo']==True,  'profit') / 1e9
pct_promo         = df['has_promo'].mean() * 100
profit_urban      = df[df['is_urban']]['profit'].sum() / 1e6

kpi_data = [
    ("TỔNG SỐ ĐƠN HÀNG",       f"{orders['order_id'].nunique():,}",  f"{df['customer_id'].nunique():,} khách hàng", COLOR_1),
    ("ĐƠN HÀNG CÓ KHUYẾN MÃI",     f"{pct_promo:.1f}%",          f"{df['has_promo'].sum():,} dòng",        COLOR_1),
    ("LỢI NHUẬN KHÔNG KHUYẾN MÃI",  f"+{profit_no_promo:.2f}B",  f"Biên lợi nhuận: {margin_no_promo*100:.1f}%",   COLOR_3),
    ("LỢI NHUẬN CÓ KHUYẾN MÃI",     f"{profit_with_promo:.2f}B", f"Biên lợi nhuận: {margin_with_promo*100:.1f}%", COLOR_2),
]

k_cols = st.columns(4)
for col, (label, val, sub, accent) in zip(k_cols, kpi_data):
    with col:
        st.markdown(f"""
        <div style="background:#ffffff; border-radius:10px; padding:10px 12px;
            border-left:4px solid {accent}; text-align:center;
            box-shadow:0 2px 8px rgba(35,25,66,0.08); margin-bottom:6px;">
            <p style="color:{TEXT_COLOR} !important; font-size:0.8rem; font-weight:600;
                letter-spacing:0.06em; margin:0 0 4px 0;">{label}</p>
            <p style="color:{accent} !important; font-size:1.6rem; font-weight:800;
                margin:0 0 2px 0; line-height:1;">{val}</p>
            <p style="color:{TEXT_COLOR} !important; font-size:0.9rem; margin:0;">{sub}</p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════
col_charts, col_side = st.columns([3, 1])

with col_charts:
    # ── ROW 1: Chart 1 | Chart 2 | Chart 3 ────
    r1a, r1b, r1c = st.columns(3)

    with r1a:
        section_title("So sánh KM và Không KM")
        summary2 = summary.copy()
        summary2['label'] = summary2['has_promo'].map({False:'Không KM', True:'Có KM'})
        fig1 = px.bar(summary2, x='label', y='margin', color='label',
            color_discrete_map={'Không KM': COLOR_3, 'Có KM': COLOR_1},
            text=summary2['margin'].apply(lambda x: f'{x*100:.1f}%'),
            labels={'label':'', 'margin':'Biên lợi nhuận gộp (%)'})
        fig1.update_traces(textposition='outside', textfont=dict(size=12))
        fig1 = apply_chart_style(fig1)
        fig1.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig1, use_container_width=True)
        insight_box("Đơn hàng có KM đang lỗ (-12.8%), trong khi không KM có lãi tốt(20.8%).Cần xác định KM nào là thủ phạm chính.", 'error')

    with r1b:
        section_title("Top 5 chương trình khuyến mãi lỗ nhiều nhất")
        promo_perf = df[df['has_promo']].groupby('promo_id').agg({'revenue':'sum','profit':'sum'}).reset_index()
        promo_perf['margin'] = promo_perf['profit'] / promo_perf['revenue'] * 100
        promo_perf = promo_perf.merge(promotions[['promo_id','promo_name']], on='promo_id').sort_values('margin').head(5)
        fig2 = px.bar(promo_perf, x='margin', y='promo_name', orientation='h',
            color_discrete_sequence=[COLOR_1],
            text=promo_perf['margin'].apply(lambda x: f'{x:.1f}%'),
            labels={'margin':'Lợi nhuận (%)','promo_name':'Chiến dịch'})
        fig2.update_traces(textposition='inside', textfont=dict(size = 12))
        fig2 = apply_chart_style(fig2)
        st.plotly_chart(fig2, use_container_width=True)
        insight_box("5 KM lỗ nhất toàn bộ là URBAN BLOWOUT (~60%). Cần tập trung phân tích chiến dịch này.", 'error')

    with r1c:
        
        section_title("Chẩn đoán tại sao URBAN BLOWOUT lỗ?")

        # ===== DATA =====
        ratio_u = df[df['is_urban']]['price_ratio'].mean() * 100
        ratio_other = df[df['has_promo'] & ~df['is_urban']]['price_ratio'].mean() * 100
        
        labels = ['Không KM', 'KM khác', 'URBAN BLOWOUT']
        values = [100, ratio_other, ratio_u]
        
        # =====  TÍNH CALLOUT =====
        # ===== CALLOUT DATA ĐÚNG THEO MẪU =====
        urban = df[df['is_urban']].copy()
        
        urban_products_check = products[
            products['product_id'].isin(
                urban['product_id'].unique()
            )
        ].copy()
        
        urban_products_check['lai_goc_tien'] = (
            urban_products_check['price']
            - urban_products_check['cogs']
        )
        
        urban_products_check['margin_goc'] = (
            urban_products_check['lai_goc_tien']
            / urban_products_check['price']
        ) * 100
        
        n_products = urban_products_check['product_id'].nunique()
        
        n_products_below_50 = (
            urban_products_check['lai_goc_tien'] < 50
        ).sum()
        
        pct_below_50 = (
            urban_products_check['margin_goc'] < 50
        ).mean() * 100
        
        # ===== BAR =====
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=labels,
            y=values,
            marker_color=[COLOR_3, COLOR_2, COLOR_1],
            text=[f'{v:.0f}%' for v in values],
            textposition='outside',
            textfont=dict(size=9)
        ))
        
        # ===== LINE: 100% =====
        fig3.add_hline(
            y=100,
            line_dash='dash',
            line_color='gray',
            line_width=1,
            annotation_text='100%',
            annotation_position='top right'
        )
        
        # ===== LINE: 50% =====
        fig3.add_hline(
            y=50,
            line_dash='dash',
            line_color=COLOR_1,
            line_width=1.5
        )
        
        # ===== VÙNG LỖ =====
        fig3.add_shape(
            type="rect",
            x0=-0.5, x1=2.5,
            y0=0, y1=50,
            fillcolor="rgba(255, 0, 0, 0.05)",
            line=dict(width=0),
            layer="below"
        )
        
        # =====  CALLOUT MỚI (REPORT STYLE) =====
        # =====  CALLOUT MỚI (KHÔNG CHE BIỂU ĐỒ) =====
        textstr = f"""
<b>⚠️ PHÁT HIỆN:</b><br><br>
• {n_products_below_50}/{n_products} sản phẩm<br>
&nbsp;&nbsp;&nbsp;&nbsp;có lãi gốc &lt; 50đ<br><br>

• {pct_below_50:.0f}% sản phẩm<br>
&nbsp;&nbsp;&nbsp;&nbsp;có margin gốc &lt; 50%
"""
        
        fig3.add_annotation(
            x=1.02,          # nằm ngoài chart bên phải
            y=0.95,
            xref='paper',
            yref='paper',
            text=textstr,
            showarrow=False,
            align='left',
            bordercolor=COLOR_1,
            borderwidth=1,
            bgcolor='rgba(255,255,255,0.95)',
            font=dict(size=9, color=DARK_TEXT),
            xanchor='left',
            yanchor='top'
        )
        
        # ===== STYLE =====
        
        
        fig3.update_layout(
            yaxis_title='Tỷ lệ giá bán (%)',
            xaxis_title='Loại chương trình'
               # tăng lề phải để chứa callout
        )
        fig3 = apply_chart_style(fig3, height=210)
        fig3.update_layout(margin=dict(l=4, r=95, t=20, b=8))
        
        
        
        fig3.update_yaxes(range=[0, 110])
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # ===== INSIGHT =====
        insight_box(
            "URBAN BLOWOUT bán ~50% giá gốc, 100% sản phẩm có margin gốc < 50%. Do lỗ cấu trúc, KHÔNG phải do discount 50đ!",'error'
        )

    # ── ROW 2: Chart 4a | Chart 4b | Chart 5 ──
    left_block, r2c = st.columns([2,2])

    with left_block:
        st.markdown(f"""
        <p style="
            color:{COLOR_1};
            font-size:0.85rem;
            font-weight:700;
            letter-spacing:0.04em;
            margin:4px 0 6px 0;
            border-bottom:1px solid rgba(94,84,142,0.2);
            text-align:center;">
            Khách hàng Urban Blowout - Trung thành & Chất lượng
        </p>
        """, unsafe_allow_html=True)

    
        r2a, r2b = st.columns(2)
    
        # ── ROW 2: Chart 4a | Chart 4b ─────────────────────
    # ── ROW 2: Chart 4a | Chart 4b ─────────────────────
        # =====================================================
    # RETENTION ANALYSIS
    # =====================================================
    
    
    # =====================================================
    # CHART 4A — STORYTELLING DUMBBELL
    # =====================================================
        with r2a:
            st.markdown(f"""
    <p style="
    font-size:0.75rem;
    font-weight:600;
    color:{DARK_TEXT};
    text-align:center;">
    Số lượng đơn hàng 
    </p>
    """, unsafe_allow_html=True)
        
            # DATA
            # khách Urban
            urban_orders = orders[
                orders['order_id'].isin(df[df['is_urban']]['order_id'].unique())
            ]
            
            urban_customers = urban_orders['customer_id'].unique()
            
            # khách không promo
            non_promo_orders = orders[
                ~orders['order_id'].isin(df[df['has_promo']]['order_id'].unique())
            ]
            
            non_promo_customers = non_promo_orders['customer_id'].unique()
            
            # avg orders/customer
            avg_u = orders[
                orders['customer_id'].isin(urban_customers)
            ].groupby('customer_id').size().mean()
            
            avg_np = orders[
                orders['customer_id'].isin(non_promo_customers)
            ].groupby('customer_id').size().mean()
            
            lift = (avg_u - avg_np) / avg_np * 100
        
            # FIGURE
            fig4a = go.Figure()
        
            # baseline line
            fig4a.add_trace(go.Scatter(
                x=[avg_np, avg_u],
                y=[0, 0],
                mode='lines',
                line=dict(color='gray', width=4),
                hoverinfo='skip',
                showlegend=False
            ))
        
            # point thường
            fig4a.add_trace(go.Scatter(
                x=[avg_np],
                y=[0],
                mode='markers+text',
                marker=dict(size=18, color=COLOR_3),
                text=[f"Thường<br>{avg_np:.1f} đơn"],
                textposition='top center',
                textfont=dict(size=10, color=DARK_TEXT),
                showlegend=False
            ))
        
            # point Urban
            fig4a.add_trace(go.Scatter(
                x=[avg_u],
                y=[0],
                mode='markers+text',
                marker=dict(size=18, color=COLOR_1),
                text=[f"Urban<br>{avg_u:.1f} đơn"],
                textposition='top center',
                textfont=dict(size=10, color=DARK_TEXT),
                showlegend=False
            ))
        
            # double arrow
            fig4a.add_annotation(
                x=avg_u,
                y=0.12,
                ax=avg_np,
                ay=0.12,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowside='end+start',
                arrowwidth=1.8,
                arrowcolor=COLOR_2
            )
        
            # % uplift
            fig4a.add_annotation(
                x=(avg_np + avg_u)/2,
                y=0.18,
                text=f"+{lift:.0f}%",
                showarrow=False,
                font=dict(size=11, color=COLOR_2)
            )
        
            
        
            fig4a.update_layout(
                xaxis_title="Số đơn trung bình mỗi khách",
                yaxis=dict(
                    visible=False,
                    range=[-0.15, 0.28]
                )
                
            )
            fig4a = apply_chart_style(fig4a, height=220)
            fig4a.update_layout(margin=dict(l=5, r=5, t=20, b=35))
        
            fig4a.update_xaxes(
                range=[avg_np - 2, avg_u + 2]
            )
            
        
            st.plotly_chart(fig4a, use_container_width=True)
            insight_box(
                f"Khách Urban mua nhiều hơn {lift:.0f}% so với khách thường.",
                "info"
            )
        
        
        # =====================================================
        # CHART 4B — CUSTOMER QUALITY
        # =====================================================
        with r2b:
            st.markdown(f"""
            <p style="font-size:0.75rem; font-weight:600;
            text-align:center;
            color:{DARK_TEXT};">
            Chất lượng khách Urban
            </p>
            """, unsafe_allow_html=True)
            
            # 1. Tệp khách hàng đã từng dùng Urban Blowout
            urban_customers = df[df['is_urban']]['customer_id'].unique()
            
            # 2. Logic Cột 1: Tỷ lệ khách Urban có phát sinh ít nhất 1 đơn hàng KHÔNG promo
            # (Mua cả không promo)
            customers_with_non_promo = df[
                (df['customer_id'].isin(urban_customers)) & 
                (df['has_promo'] == False)
            ]['customer_id'].nunique()
            pct_quality = (customers_with_non_promo / len(urban_customers)) * 100

            # 3. Logic Cột 2: Tỷ lệ đơn hàng không promo trên TỔNG số đơn của nhóm khách Urban này
            # (Đơn không promo)
            urban_customers_all_orders = orders[orders['customer_id'].isin(urban_customers)]
            total_orders_urban = len(urban_customers_all_orders)
            
            # Đếm đơn không promo của họ
            promo_order_ids = df[df['has_promo'] == True]['order_id'].unique()
            non_promo_urban_orders_count = len(urban_customers_all_orders[~urban_customers_all_orders['order_id'].isin(promo_order_ids)])
            pct_orders = (non_promo_urban_orders_count / total_orders_urban) * 100

            # FIGURE
            fig4b = go.Figure()
            fig4b.add_trace(go.Bar(
                x=['Mua cả không KM', 'Đơn không KM'],
                y=[pct_quality, pct_orders],
                marker_color=[COLOR_1, COLOR_2],
                text=[f'{pct_quality:.1f}%', f'{pct_orders:.1f}%'],
                textposition='outside',
                width=0.5 # Chỉnh thanh bar gọn lại cho giống mẫu của bạn
            ))

            

            # STYLE
            
            fig4b.update_layout(
                
                yaxis_title='Tỷ lệ (%)'
            )
            fig4b = apply_chart_style(fig4b, height=220)
            fig4b.update_layout(margin=dict(l=5, r=5, t=25, b=35))
            fig4b.update_yaxes(range=[0, 115]) # Để không bị mất label 92.6% ở trên đầu
            fig4b.update_xaxes(tickfont=dict(size=10))

            st.plotly_chart(fig4b, use_container_width=True)
            insight_box("92.6% khách URBAN BLOWOUT vẫn mua giá gốc. Đây là khách trung thành, không nghiện giảm giá. Cần tăng giá ngay để cắt lỗ", "success")

        with r2c:
            section_title("Dự báo tác động của thay đổi giá")
        
            urban_df = df[df['is_urban']].copy()
        
            # CURRENT
            urban_df['profit_current'] = urban_df['profit']
        
            # NEW 90%
            urban_df['new_revenue'] = urban_df['quantity'] * urban_df['price'] * 0.9
            urban_df['new_profit'] = (
                urban_df['new_revenue']
                - urban_df['cogs_total']
                - urban_df['discount_amount']
            )
        
            # GROUP YEAR
            by_year = urban_df.groupby('year').agg(
                profit_current=('profit_current', 'sum'),
                profit_new=('new_profit', 'sum')
            ).reset_index()
        
            by_year_full = by_year[by_year['year'] < 2022].sort_values('year')
        
            avg_current = by_year_full.tail(2)['profit_current'].mean()
            avg_new = by_year_full.tail(2)['profit_new'].mean()
        
            future_years = list(range(2023, 2030))
            future_current = [avg_current] * len(future_years)
            future_new = [avg_new] * len(future_years)
        
            hist_years = list(by_year_full['year'])
            all_years = hist_years + future_years
        
            all_profit_current = list(by_year_full['profit_current']) + future_current
            all_profit_new = list(by_year_full['profit_new']) + future_new
        
            cum_current = np.cumsum(all_profit_current)
            cum_new = np.cumsum(all_profit_new)
        
            n_hist = len(hist_years)
        
            fig5 = go.Figure()
        
            # LINE A
            fig5.add_trace(go.Scatter(
                x=all_years[:n_hist],
                y=np.array(cum_current[:n_hist]) / 1e6,
                mode='lines+markers',
                name='Kịch bản A: 50%',
                line=dict(color=COLOR_1, width=3)
            ))
        
            fig5.add_trace(go.Scatter(
                x=all_years[n_hist-1:],
                y=np.array(cum_current[n_hist-1:]) / 1e6,
                mode='lines',
                line=dict(color=COLOR_1, width=2, dash='dash'),
                showlegend=False
            ))
        
            # LINE B
            fig5.add_trace(go.Scatter(
                x=all_years[:n_hist],
                y=np.array(cum_new[:n_hist]) / 1e6,
                mode='lines+markers',
                name='Kịch bản B: 90%',
                line=dict(color=COLOR_2, width=3)
            ))
        
            fig5.add_trace(go.Scatter(
                x=all_years[n_hist-1:],
                y=np.array(cum_new[n_hist-1:]) / 1e6,
                mode='lines',
                line=dict(color=COLOR_2, width=2, dash='dash'),
                showlegend=False
            ))
        
            # FILL GAP
            fig5.add_trace(go.Scatter(
                x=all_years,
                y=np.array(cum_new) / 1e6,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
        
            fig5.add_trace(go.Scatter(
                x=all_years,
                y=np.array(cum_current) / 1e6,
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(216,85,162,0.18)',
                line=dict(width=0),
                showlegend=False
            ))
        
            # BASE LINES
            fig5.add_hline(y=0, line_dash='dash', line_color='gray')
            fig5.add_vline(x=2022, line_dash='dot', line_color='gray')
        
            gap = (cum_new[-1] - cum_current[-1]) / 1e6
        
            # ===== LABEL CUỐI LINE TRÊN =====
            fig5.add_annotation(
                x=2029.25,
                y=cum_new[-1] / 1e6,
                text=f"{cum_new[-1]/1e6:.0f}M",
                showarrow=False,
                font=dict(color=COLOR_2, size=11)
            )
        
            # ===== LABEL CUỐI LINE DƯỚI =====
            fig5.add_annotation(
                x=2029.25,
                y=cum_current[-1] / 1e6,
                text=f"{cum_current[-1]/1e6:.0f}M",
                showarrow=False,
                font=dict(color=COLOR_1, size=11)
            )
        
            # ===== ARROW GAP =====
            fig5.add_annotation(
                x=2029,
                y=cum_new[-1]/1e6,
                ax=2029,
                ay=cum_current[-1]/1e6,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowside='end+start',
                arrowcolor='gray'
            )
        
            # GAP TEXT
            fig5.add_annotation(
                x=2029.75,
                y=(cum_new[-1] + cum_current[-1]) / 2 / 1e6,
                text=f"+{gap:.0f}M",
                showarrow=False,
                font=dict(color='gray', size=11)
            )
            fig5.update_layout( xaxis_title="Năm", yaxis_title="Lợi nhuận tích lũy (Triệu VND)")
            fig5 = apply_chart_style(fig5, height = 260)
            fig5.update_layout(showlegend=True, legend=dict(orientation='h', x=0.5, xanchor='center',y=1.25, font=dict(color=DARK_TEXT, size=11)), margin=dict(l=10, r=40, t=60, b=40))
        
            st.plotly_chart(fig5, use_container_width=True)
        
            insight_box(
                f"Tăng giá lên 90% giá gốc giúp xoay chuyển tình thế từ lỗ 492 triệu thành lãi 135 triệu VND. Tổng lợi nhuận cải thiện thêm 627 triệu VND, chứng minh hiệu quả kinh tế vượt trội so với mức giá 50% hiện tại." ,"success"
            )

   
        
# ============================================================
# CHART 5: DỰ BÁO KỊCH BẢN GIÁ
# ============================================================
# ============================================================
# CHART 5: DỰ BÁO KỊCH BẢN GIÁ
# ============================================================
    
       
        
# ──────────────────────────────────────────────
# SIDEBAR PHẢI
# ──────────────────────────────────────────────
with col_side:
    section_title(" Đề xuất hành động")
    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.75rem; color:{DARK_TEXT};">
        <thead>
            <tr style="background:{COLOR_1}; color:#ffffff;">
                <th style="padding:6px 5px; text-align:center; width:16px;">#</th>
                <th style="padding:6px 5px; text-align:left;">Hành động</th>
                <th style="padding:6px 5px; text-align:left;">Người thực hiện</th>
                <th style="padding:6px 5px; text-align:left;">Thời gian</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background:#ffffff; border-bottom:1px solid #e2e2e2;">
                <td style="padding:7px 5px; text-align:center; color:{COLOR_1}; font-weight:700;">1</td>
                <td style="padding:7px 5px;"><strong>Tăng giá URBAN BLOWOUT 50% → 90% giá gốc</strong></td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Team Marketing và Team Pricing</td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Quý tới</td>
            </tr>
            <tr style="background:#fcfcff; border-bottom:1px solid #e2e2e2;">
                <td style="padding:7px 5px; text-align:center; color:{COLOR_1}; font-weight:700;">2</td>
                <td style="padding:7px 5px;"><strong>Giới hạn chiết khấu ~40%</strong></td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Ban giám đốc</td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Ngay khi duyệt</td>
            </tr>
            <tr style="background:#ffffff;">
                <td style="padding:7px 5px; text-align:center; color:{COLOR_1}; font-weight:700;">3</td>
                <td style="padding:7px 5px;"><strong>Biến URBAN BLOWOUT chương trình tri ân cho VIP</strong></td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Team CRM/td>
                <td style="padding:7px 5px; color:{TEXT_COLOR};">Tháng sau</td>
            </tr>
        </tbody>
    </table>
    <div style="background:#e8f5e9; border-radius:6px; padding:8px 10px;
        border-left:3px solid #4caf50; margin-top:8px;">
        <p style="color:#1b5e20 !important; font-size:0.72rem; margin:0;">
            <strong>✓ Kỳ vọng:</strong> Thu hồi 487 triệu VND lợi nhuận bị mất.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)

    section_title("Kết luận")
    for accent, label, text in [
    (COLOR_1, "Mô tả:", "Đơn hàng có KM gây lỗ 678 triệu VND, chủ yếu là URBAN BLOWOUT (TOP5 chiến dịch lỗ nhất)."),

    (COLOR_1, "Chẩn đoán:",
     "Lỗ cấu trúc do bán chỉ 50% so với giá gốc, margin thấp. "
     "Không nên cắt URBAN BLOWOUT vì nhóm khách hàng siêu trung thành (92.6% mua cả khi không có KM)."),

    (COLOR_1, "Dự báo:",
     "Nếu tăng giá lên 90% so với giá gốc → lãi tích lũy 135 triệu VND."),

    (COLOR_1, "Đề xuất:",
     "Tăng giá Quý tới + chuyển Urban thành đặc quyền VIP.")
]:
        st.markdown(f"""
        <div style="background:#ffffff; border-radius:6px; padding:8px 10px;
            border-left:3px solid {accent}; margin-bottom:6px;
            box-shadow:0 1px 4px rgba(35,25,66,0.05);">
            <p style="color:{accent} !important; font-size:0.68rem; font-weight:700; margin:0 0 2px 0;">{label}</p>
            <p style="color:{TEXT_COLOR} !important; font-size:0.7rem; margin:0; line-height:1.4;">{text}</p>
        </div>""", unsafe_allow_html=True)