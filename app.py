import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLE ---
st.set_page_config(page_title="My Trading Portfolio", page_icon="🌊", layout="wide")

# ชุดสี Pastel Theme
THEME = {
    "Background": "#E3F4F6",
    "SidebarBg": "#B9D7EA",
    "CardBg": "#FFFFFF",
    "Text": "#2C3E50",
    "Mint": "#27AE60",  # เขียวเข้ม
    "Red": "#E74C3C",  # <--- สีแดงสำหรับค่าติดลบ
    "Cream": "#FCDEC1",
    "Pink": "#F17784",
    "Blue": "#5DADE2",
    "Grey": "#A5A5A5"
}

# 🎨 CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {THEME['Background']}; }}
    header[data-testid="stHeader"] {{ background-color: {THEME['Background']}; }}
    section[data-testid="stSidebar"] {{ background-color: {THEME['SidebarBg']}; }}

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label {{ color: #1A5276 !important; }}

    div[role="radiogroup"] > label > div:first-child {{
        background-color: #FFFFFF;
        border: 1px solid #1A5276;
    }}

    .metric-card {{
        background-color: {THEME['CardBg']};
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 2px solid white;
        height: 100%;
    }}
    .metric-label {{ font-size: 14px; color: #7F8C8D; font-weight: 500; margin-bottom: 5px; }}
    .metric-value {{ font-size: 26px; color: {THEME['Text']}; font-weight: 700; }}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LINKS ---
MONTH_LINKS = {
    "มกราคม 69": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRYsFTD4K-tyIFIJry2YLJtnv6gUxZy9VZCvRZcOeGrD9X7inE8udy-cJU_ajJEWcouDSswJZYdAjE8/pub?output=csv",
    "ธันวาคม 68": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmtzNSKaXCSpk03ahtml7UAOHCIz_P8FKe95Lot20_RTARgHj0Ev1bcdFgjUWS6QtwENnlzQ3IjIAX/pub?gid=1875855074&single=true&output=csv",
    "พฤศจิกายน 68": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmtzNSKaXCSpk03ahtml7UAOHCIz_P8FKe95Lot20_RTARgHj0Ev1bcdFgjUWS6QtwENnlzQ3IjIAX/pub?gid=902579377&single=true&output=csv",
    "-": "ใส่_LINK_กพ_ตรงนี้",
}


@st.cache_data(ttl=60)
def load_data(url):
    try:
        if "ใส่_LINK" in url or url is None: return pd.DataFrame()
        data = pd.read_csv(url)
        return data
    except:
        return pd.DataFrame()


def parse(val):
    try:
        return float(str(val).replace(',', ''))
    except:
        return 0.0


def fmt(val): return f"{parse(val):,.2f}"


# --- 3. SIDEBAR ---
st.sidebar.title("🌊 Blue Vibe")
app_mode = st.sidebar.radio("เลือกโหมดการดูข้อมูล",
                            ["📅 ดูรายเดือน", "📊 ภาพรวมทุกเดือน (Summary)"],
                            index=0)
st.sidebar.markdown("---")

if app_mode == "📅 ดูรายเดือน":
    selected_month = st.sidebar.selectbox("เลือกเดือน", list(MONTH_LINKS.keys()))
    selected_url = MONTH_LINKS[selected_month]
else:
    selected_month = "Summary"

if st.sidebar.button('🔄 รีเฟรชข้อมูล'):
    st.cache_data.clear()
    st.rerun()

# --- 4. LOGIC & UI ---

# === VIEW: SUMMARY ===
if app_mode == "📊 ภาพรวมทุกเดือน (Summary)":
    st.title("📊 ภาพรวมทุกเดือน (Summary)")
    st.markdown("---")

    all_months_data = []
    progress_text = st.empty()
    progress_text.text("⏳ กำลังโหลดข้อมูลเทรนด์...")

    for month_name, url in MONTH_LINKS.items():
        if url and "http" in url:
            df = load_data(url)
            if not df.empty:
                try:
                    row = df.iloc[0]
                    all_months_data.append({
                        "Month": month_name,
                        "Balance": parse(row.get('วงเงินปัจจุบัน', 0)),
                        "Profit": parse(row.get('กำไร', 0)),
                        "Withdraw": parse(row.get('เบิก', 0)),
                        "Scam": parse(df.iloc[0, 16]) if len(df.columns) > 16 else parse(row.get('ต้นที่โดนบิด', 0)),
                        "Net": parse(row.get('กำไรสุทธิ', 0))
                    })
                except:
                    continue

    progress_text.empty()

    if all_months_data:
        df_all = pd.DataFrame(all_months_data)
        total_profit = df_all['Profit'].sum()
        total_withdraw = df_all['Withdraw'].sum()
        total_scam = df_all['Scam'].sum()
        total_net = df_all['Net'].sum()
        latest_balance = df_all.iloc[0]['Balance']


        def card(label, value, text_color):
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color: {text_color};">{value}</div>
            </div>
            """, unsafe_allow_html=True)


        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            card("💰 วงเงินล่าสุด", fmt(latest_balance), THEME["Text"])
        with c2:
            card("💵 กำไรสะสม", fmt(total_profit), THEME["Mint"])
        with c3:
            card("💸 เบิกสะสม", fmt(total_withdraw), "#F5B041")
        with c4:
            card("🥀 โดนบิดรวม", fmt(total_scam), THEME["Pink"])
        with c5:
            card("🌱 กำไรสุทธิรวม", fmt(total_net), THEME["Blue"])

        st.markdown("###")

        col_chart, col_data = st.columns([2, 1])
        with col_chart:
            st.subheader("📈 แนวโน้มกำไรรายเดือน (Monthly Trend)")
            df_chart = df_all.iloc[::-1]
            fig_trend = px.line(df_chart, x='Month', y=['Profit', 'Net'],
                                markers=True,
                                color_discrete_sequence=[THEME['Mint'], THEME['Blue']],
                                labels={'value': 'Amount (THB)', 'variable': 'Type'})
            fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#2C3E50",
                                    legend_title_text='', xaxis_title=None)
            fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_data:
            st.subheader("📄 ข้อมูลรายเดือน")
            st.dataframe(df_all[['Month', 'Profit', 'Net', 'Withdraw']])
    else:
        st.warning("ไม่พบข้อมูล")

# === VIEW: SINGLE MONTH ===
else:
    st.title(f"📊 Dashboard: {selected_month}")
    st.markdown("---")

    df = load_data(selected_url)

    if not df.empty:
        try:
            row = df.iloc[0]

            profit = parse(row.get('กำไร', 0))
            withdraw = parse(row.get('เบิก', 0))
            net_profit = parse(row.get('กำไรสุทธิ', 0))
            balance = parse(row.get('วงเงินปัจจุบัน', 0))
            pct_profit_str = str(row.get('%กำไร', '0%'))

            scam_principal = 0
            try:
                if len(df.columns) > 16:
                    scam_principal = parse(df.iloc[0, 16])
                else:
                    scam_principal = parse(row.get('ต้นที่โดนบิด', 0))
            except:
                scam_principal = 0

            # --- Logic เปลี่ยนสี % กำไร ---
            hero_color = THEME['Mint']  # ค่าเริ่มต้น: เขียว
            try:
                # แปลงเป็นตัวเลขเพื่อเช็คค่าลบ (ตัด % และ , ออก)
                pct_val = float(pct_profit_str.replace('%', '').replace(',', ''))
                if pct_val < 0:
                    hero_color = THEME['Red']  # ถ้าติดลบ ให้เป็นสีแดง
            except:
                pass
                # ---------------------------

            # Hero Metric (แสดงผลด้วยสีที่คำนวณมา)
            hm1, hm2, hm3 = st.columns([1, 2, 1])
            with hm2:
                st.markdown(f"""
                <div style="
                    background-color: #FFFFFF;
                    border-radius: 20px;
                    padding: 15px;
                    margin-bottom: 25px;
                    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
                    text-align: center;
                    border: 3px solid {hero_color}; /* สีขอบเปลี่ยนตามค่า */
                ">
                    <div style="font-size: 16px; color: #7F8C8D; margin-bottom: 5px;">🚀 % กำไรเติบโต (% Growth)</div>
                    <div style="font-size: 50px; font-weight: 800; color: {hero_color}; line-height: 1;"> {pct_profit_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)


            def card(label, value, text_color):
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color: {text_color};">{value}</div>
                </div>
                """, unsafe_allow_html=True)


            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                card("💰 วงเงินปัจจุบัน", fmt(balance), THEME["Text"])
            with c2:
                card("💵 กำไร (Gross)", fmt(profit), THEME["Mint"])
            with c3:
                card("💸 เบิกแล้ว", fmt(withdraw), "#F5B041")
            with c4:
                card("🥀 ต้นที่โดนบิด", fmt(scam_principal), THEME["Pink"])
            with c5:
                card("🌱 กำไรสุทธิ", fmt(net_profit), THEME["Blue"])

            st.markdown("###")

            col_bar, col_pie = st.columns([2, 1])
            with col_bar:
                st.subheader("กราฟแท่งเปรียบเทียบ")
                items = ['กำไร', 'เบิก', 'ต้นที่โดนบิด', 'กำไรสุทธิ']
                vals = [profit, withdraw, scam_principal, net_profit]
                colors = [THEME["Mint"], THEME["Cream"], THEME["Pink"], THEME["Blue"]]
                bar_df = pd.DataFrame({'รายการ': items, 'บาท': vals, 'Color': colors})
                fig_bar = px.bar(bar_df, x='รายการ', y='บาท',
                                 text_auto='.2s', color='รายการ',
                                 color_discrete_sequence=colors)
                fig_bar.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                      font_color="#2C3E50")
                fig_bar.update_traces(textfont_size=14, cliponaxis=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_pie:
                st.subheader("สัดส่วนพอร์ต")
                cost = balance - profit
                pie_df = pd.DataFrame({'Type': ['ต้นทุน', 'กำไร'], 'Value': [cost, profit]})
                fig_pie = px.pie(pie_df, values='Value', names='Type',
                                 color_discrete_sequence=[THEME["Grey"], THEME["Mint"]], hole=0.6)
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                                      legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
                st.plotly_chart(fig_pie, use_container_width=True)

            with st.expander("📄 ดูข้อมูลดิบ"):
                st.dataframe(df)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.info("กำลังโหลดข้อมูล...")