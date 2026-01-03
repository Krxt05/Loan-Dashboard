import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import re

# --- 1. SETTINGS & STYLE ---
st.set_page_config(page_title="My Loan Portfolio", page_icon="🌊", layout="wide")

# ชุดสี Pastel Theme
THEME = {
    "Background": "#E3F4F6",
    "SidebarBg": "#B9D7EA",
    "CardBg": "#FFFFFF",
    "Text": "#2C3E50",
    "Mint": "#27AE60",
    "Red": "#E74C3C",
    "Cream": "#FCDEC1",
    "Pink": "#F17784",
    "Blue": "#5DADE2",
    "Grey": "#A5A5A5"
}

# CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {THEME['Background']}; }}
    header[data-testid="stHeader"] {{ background-color: {THEME['Background']}; }}
    section[data-testid="stSidebar"] {{ background-color: {THEME['SidebarBg']}; }}

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label {{ color: #1A5276 !important; }}

    /* Cards */
    .metric-card {{
        background-color: {THEME['CardBg']};
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 2px solid white;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        cursor: default;
    }}
    .metric-card:hover {{
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0px 15px 30px rgba(0,0,0,0.15);
        border-color: {THEME['Blue']};
        z-index: 10;
    }}
    .metric-label {{ font-size: 14px; color: #7F8C8D; font-weight: 500; margin-bottom: 5px; }}
    .metric-value {{ font-size: 24px; color: {THEME['Text']}; font-weight: 700; }}

    /* Hero Card */
    .hero-card {{
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-width: 3px;
        border-style: solid;
        transition: all 0.3s ease;
    }}
    .hero-card:hover {{ transform: scale(1.03); box-shadow: 0px 10px 25px rgba(0,0,0,0.2); }}

    /* Inputs */
    div[data-testid="stSelectbox"] {{
        background-color: #FFFFFF;
        border: 3px solid {THEME['Mint']};
        border-radius: 15px;
        padding: 10px 15px;
        box-shadow: 0px 4px 20px rgba(39, 174, 96, 0.3);
        transition: all 0.3s ease;
    }}
    div[data-testid="stSelectbox"]:hover {{ box-shadow: 0px 6px 25px rgba(39, 174, 96, 0.5); transform: translateY(-2px); }}
    div[data-testid="stSelectbox"] label {{ font-size: 20px !important; color: {THEME['Mint']} !important; font-weight: 900 !important; }}

    div[data-testid="stDateInput"] {{
        background-color: #FFFFFF;
        border: 2px solid {THEME['Blue']};
        border-radius: 15px;
        padding: 5px 15px;
        box-shadow: 0px 2px 10px rgba(93, 173, 226, 0.2);
        transition: all 0.2s ease;
    }}
    div[data-testid="stDateInput"]:hover {{ transform: scale(1.02); }}
    div[data-testid="stDateInput"] label {{ font-size: 16px !important; color: {THEME['Blue']} !important; font-weight: bold !important; }}

    div[data-testid="stSelectbox"] *, div[data-testid="stDateInput"] * {{ cursor: pointer !important; }}
    div[data-testid="stSelectbox"] input, div[data-testid="stDateInput"] input {{ caret-color: transparent !important; cursor: pointer !important; }}

    /* Tabs Customization (Fixed Braces) */
    button[data-baseweb="tab"] {{
        font-size: 18px;
        font-weight: 600;
    }}

</style>
""", unsafe_allow_html=True)

# --- 2. DATA LINKS ---
MONTH_LINKS = {
    "มกราคม 69": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRYsFTD4K-tyIFIJry2YLJtnv6gUxZy9VZCvRZcOeGrD9X7inE8udy-cJU_ajJEWcouDSswJZYdAjE8/pub?output=csv",
    "ธันวาคม 68": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmtzNSKaXCSpk03ahtml7UAOHCIz_P8FKe95Lot20_RTARgHj0Ev1bcdFgjUWS6QtwENnlzQ3IjIAX/pub?gid=1875855074&single=true&output=csv",
    "พฤศจิกายน 68": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmtzNSKaXCSpk03ahtml7UAOHCIz_P8FKe95Lot20_RTARgHj0Ev1bcdFgjUWS6QtwENnlzQ3IjIAX/pub?gid=902579377&single=true&output=csv",
    "-": "ใส่_LINK_กพ_ตรงนี้",
}

COL_IDX = {
    "id": 0, "name": 1, "principal": 2, "due_date": 4,
    "interest": 9, "penalty": 10, "status": 12,
    "actual_date": 5, "actual_interest": 15
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


def parse_thai_date(val):
    try:
        s = str(val).strip()
        if not s or s.lower() == 'nan': return pd.NaT
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if pd.isnull(dt):
            parts = s.replace('-', '/').split('/')
            if len(parts) == 3:
                d, m, y = parts[0], parts[1], parts[2]
                if int(y) > 2400: y = int(y) - 543
                return pd.to_datetime(f"{y}-{m}-{d}", errors='coerce')
        return dt
    except:
        return pd.NaT


# --- Helper Functions ---
def extract_renewal_count(val):
    s = str(val).strip()
    if 'ต่อ' in s:
        nums = re.findall(r'\d+', s)
        if nums:
            return int(nums[0])
        else:
            return 1
    return 0


def check_is_paid(val):
    s = str(val).strip()
    if 'ชำระแล้ว' in s or 'paid' in s.lower() or 'ปิด' in s: return True
    return False


# --- 3. SIDEBAR ---
st.sidebar.title("🌊 Blue Vibe")
app_mode = st.sidebar.radio("เมนูหลัก", ["📅 ดูรายเดือน", "📊 ภาพรวมทุกเดือน (Summary)"], index=0)
st.sidebar.markdown("---")

if st.sidebar.button('🔄 รีเฟรชข้อมูล'):
    st.cache_data.clear()
    st.rerun()

# --- 4. LOGIC & UI ---

if app_mode == "📊 ภาพรวมทุกเดือน (Summary)":
    st.title("📊 ภาพรวมทุกเดือน (Summary)")
    st.markdown("---")

    all_months_data = []
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
            st.subheader("📈 แนวโน้มกำไรรายเดือน")
            df_chart = df_all.iloc[::-1]
            fig_trend = px.line(df_chart, x='Month', y=['Profit', 'Net'],
                                markers=True, color_discrete_sequence=[THEME['Mint'], THEME['Blue']])
            fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#2C3E50")
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_data:
            st.subheader("📄 ข้อมูลรายเดือน")
            st.dataframe(df_all[['Month', 'Profit', 'Net', 'Withdraw']])
    else:
        st.warning("ไม่พบข้อมูล")

else:
    # --- SINGLE MONTH VIEW ---
    col_title, col_select = st.columns([2, 1], gap="medium")

    with col_select:
        selected_month = st.selectbox("📁 เลือกเดือนที่ต้องการดูข้อมูล:", list(MONTH_LINKS.keys()))
        selected_url = MONTH_LINKS[selected_month]

    with col_title:
        st.title(f"📊 Dashboard: {selected_month}")
        try:
            th_tz = pytz.timezone('Asia/Bangkok')
            now_th = datetime.now(th_tz)
            # st.caption(f"🕒 Server Time (TH): {now_th.strftime('%d/%m/%Y %H:%M:%S')}")
        except:
            pass

    st.markdown("---")

    df = load_data(selected_url)

    if not df.empty:
        try:
            # -----------------------------------
            # PREPARE DATA
            # -----------------------------------
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

            hero_color = THEME['Mint']
            try:
                pct_val = float(pct_profit_str.replace('%', '').replace(',', ''))
                if pct_val < 0: hero_color = THEME['Red']
            except:
                pass


            def card(label, value, text_color):
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color: {text_color};">{value}</div>
                </div>""", unsafe_allow_html=True)


            # -----------------------------------
            # CREATE TABS (4 ZONES)
            # -----------------------------------
            tab1, tab2, tab3, tab4 = st.tabs([
                "💵 สรุป & ติดตาม (Financials)",
                "📊 กราฟ & ปฏิทิน (Charts)",
                "📋 ประวัติ & ค่าปรับ (History)",
                "📄 ข้อมูลดิบ (Raw Data)"
            ])

            # =======================================================
            # TAB 1: FINANCIALS & LOAN TRACKER
            # =======================================================
            with tab1:
                zone1_col, zone2_col = st.columns([1.2, 1], gap="large")

                with zone1_col:
                    st.subheader("💵 สรุปยอดเงิน (Financials)")
                    st.markdown(f"""
                    <div class="hero-card" style="border-color: {hero_color};">
                        <div style="font-size: 16px; color: #7F8C8D; margin-bottom: 5px;">🚀 % กำไรเติบโต (% Growth)</div>
                        <div style="font-size: 50px; font-weight: 800; color: {hero_color}; line-height: 1;">{pct_profit_str}</div>
                    </div>""", unsafe_allow_html=True)

                    r1_c1, r1_c2 = st.columns(2)
                    with r1_c1: card("💰 วงเงินปัจจุบัน", fmt(balance), THEME["Text"])
                    with r1_c2: card("💵 กำไร (Gross)", fmt(profit), THEME["Mint"])
                    r2_c1, r2_c2 = st.columns(2)
                    with r2_c1: card("💸 เบิกแล้ว", fmt(withdraw), "#F5B041")
                    with r2_c2: card("🥀 ต้นที่โดนบิด", fmt(scam_principal), THEME["Pink"])
                    card("🌱 กำไรสุทธิ", fmt(net_profit), THEME["Blue"])

                with zone2_col:
                    st.subheader("📅 ติดตามยอดชำระ (Loan Tracker)")
                    if len(df) > 2:
                        th_tz = pytz.timezone('Asia/Bangkok')
                        current_date_th = datetime.now(th_tz)

                        selected_date = st.date_input("เลือกวันที่:", current_date_th)
                        loan_data = df.iloc[2:].copy()
                        try:
                            tracker_df = pd.DataFrame()
                            tracker_df['id'] = loan_data.iloc[:, COL_IDX['id']]
                            tracker_df['name'] = loan_data.iloc[:, COL_IDX['name']]
                            tracker_df['principal'] = loan_data.iloc[:, COL_IDX['principal']]
                            tracker_df['due_date'] = loan_data.iloc[:, COL_IDX['due_date']]
                            tracker_df['interest'] = loan_data.iloc[:, COL_IDX['interest']]

                            tracker_df['due_date'] = tracker_df['due_date'].apply(parse_thai_date)
                            target_date = pd.Timestamp(selected_date).normalize()
                            due_target = tracker_df[tracker_df['due_date'] == target_date]

                            sum_princ = pd.to_numeric(due_target['principal'].astype(str).str.replace(',', ''),
                                                      errors='coerce').sum()
                            sum_int = pd.to_numeric(due_target['interest'].astype(str).str.replace(',', ''),
                                                    errors='coerce').sum()
                            total_target = sum_princ + sum_int

                            st.markdown(f"""
                            <div class="tracker-card">
                                <div style="font-size: 16px; color: #856404;">🔥 ยอดที่ต้องรับชำระวันที่ <br> {target_date.strftime('%d/%m/%Y')}</div>
                                <div style="font-size: 36px; font-weight: bold; color: #856404;">{fmt(total_target)}</div>
                                <div style="font-size: 16px; color: #856404; margin-top: 5px;">
                                    (เงินต้น: {fmt(sum_princ)} + <b style="color: #D35400;">ดอกเบี้ย: {fmt(sum_int)}</b>)
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            if not due_target.empty:
                                st.write(f"**รายชื่อ ({len(due_target)} ราย):**")
                                st.dataframe(due_target[['id', 'name', 'principal', 'interest']], hide_index=True,
                                             use_container_width=True)
                            else:
                                st.success(f"✅ ไม่มีรายการครบกำหนด")
                        except Exception as e:
                            st.warning(f"โหลดข้อมูล Loan Tracker ไม่ได้: {e}")
                    else:
                        st.info("ไม่มีข้อมูลลูกหนี้")

            # =======================================================
            # TAB 2: CHARTS & SCHEDULE
            # =======================================================
            with tab2:
                st.subheader("📊 กราฟแสดงผล (Charts)")
                col_bar, col_pie = st.columns([2, 1])
                with col_bar:
                    items = ['กำไร', 'เบิก', 'ต้นที่โดนบิด', 'กำไรสุทธิ']
                    vals = [profit, withdraw, scam_principal, net_profit]
                    colors = [THEME["Mint"], THEME["Cream"], THEME["Pink"], THEME["Blue"]]
                    bar_df = pd.DataFrame({'รายการ': items, 'บาท': vals, 'Color': colors})
                    fig_bar = px.bar(bar_df, x='รายการ', y='บาท', text_auto='.2s', color='รายการ',
                                     color_discrete_sequence=colors)
                    fig_bar.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                          font_color="#2C3E50")
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col_pie:
                    cost = balance - profit
                    pie_df = pd.DataFrame({'Type': ['ต้นทุน', 'กำไร'], 'Value': [cost, profit]})
                    fig_pie = px.pie(pie_df, values='Value', names='Type',
                                     color_discrete_sequence=[THEME["Grey"], THEME["Mint"]], hole=0.6)
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                                          legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_pie, use_container_width=True)

                if len(df) > 2:
                    st.markdown("---")
                    st.subheader("📅 ปฏิทินรับดอกเบี้ย (Interest Schedule)")

                    cal_df = df.iloc[2:].copy()
                    try:
                        due_data = pd.DataFrame()
                        due_data['Date'] = cal_df.iloc[:, COL_IDX['due_date']].apply(parse_thai_date)
                        due_data['Amount'] = pd.to_numeric(
                            cal_df.iloc[:, COL_IDX['interest']].astype(str).str.replace(',', ''), errors='coerce')

                        actual_data = pd.DataFrame()
                        actual_data['Date'] = cal_df.iloc[:, COL_IDX['actual_date']].apply(parse_thai_date)
                        actual_data['Amount'] = pd.to_numeric(
                            cal_df.iloc[:, COL_IDX['actual_interest']].astype(str).str.replace(',', ''),
                            errors='coerce')

                        due_group = due_data.dropna(subset=['Date']).groupby('Date')['Amount'].sum().reset_index()
                        due_group['Type'] = 'คาดการณ์ (Due)'

                        actual_group = actual_data.dropna(subset=['Date']).groupby('Date')['Amount'].sum().reset_index()
                        actual_group['Type'] = 'ชำระจริง (Actual)'

                        final_chart_df = pd.concat([due_group, actual_group], ignore_index=True)
                        final_chart_df = final_chart_df.sort_values('Date')

                        if not final_chart_df.empty:
                            fig_cal = px.bar(final_chart_df, x='Date', y='Amount', color='Type',
                                             barmode='group',
                                             title="เปรียบเทียบยอดดอกเบี้ย: ครบกำหนด (เขียว) vs ได้จริง (ฟ้า)",
                                             labels={'Date': 'วันที่', 'Amount': 'ดอกเบี้ยรวม (บาท)', 'Type': 'สถานะ'},
                                             color_discrete_map={'คาดการณ์ (Due)': THEME['Mint'],
                                                                 'ชำระจริง (Actual)': THEME['Blue']},
                                             text_auto='.2s')
                            fig_cal.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                                  font_color="#2C3E50")
                            st.plotly_chart(fig_cal, use_container_width=True)
                        else:
                            st.info("ยังไม่มีข้อมูลวันที่")
                    except Exception as e:
                        st.error(f"Error: {e}")

            # =======================================================
            # TAB 3: HISTORY & PENALTY
            # =======================================================
            with tab3:
                st.subheader("📋 ประวัติและค่าปรับ (History & Penalty)")

                # เตรียมข้อมูล
                hist_df = df.iloc[2:].copy()
                hist_data = pd.DataFrame()
                hist_data['Name'] = hist_df.iloc[:, COL_IDX['name']]
                hist_data['Principal'] = hist_df.iloc[:, COL_IDX['principal']].apply(parse)
                hist_data['Interest'] = hist_df.iloc[:, COL_IDX['interest']].apply(parse)
                hist_data['Penalty'] = hist_df.iloc[:, COL_IDX['penalty']].apply(parse)

                # Logic
                hist_data['Raw_Status'] = hist_df.iloc[:, COL_IDX['status']].astype(str)
                hist_data['Row_Renewal'] = hist_data['Raw_Status'].apply(extract_renewal_count)
                hist_data['Row_Is_Paid'] = hist_data['Raw_Status'].apply(check_is_paid)

                # แบ่งคอลัมน์ ซ้าย-ขวา
                c_renew, c_penalty = st.columns(2)

                # --- ซ้าย: ประวัติการต่อดอก (Grouped) ---
                with c_renew:
                    st.markdown("##### 🔄 สรุปยอดต่อดอก (Renewals)")
                    try:
                        grouped = hist_data.groupby(['Name', 'Principal', 'Interest']).agg({
                            'Row_Renewal': 'sum',
                            'Row_Is_Paid': 'any',
                            'Raw_Status': lambda x: ' -> '.join(x.unique())
                        }).reset_index()

                        grouped['Total_Renewal_Income'] = grouped['Row_Renewal'] * grouped['Interest']


                        def get_status_text(r):
                            if r['Row_Is_Paid']: return "✅ ปิดบัญชี"
                            if r['Row_Renewal'] > 0: return f"🔄 ต่อ {r['Row_Renewal']} รอบ"
                            return "🆕 สัญญาใหม่"


                        grouped['Status_Text'] = grouped.apply(get_status_text, axis=1)

                        final_renew = grouped[(grouped['Row_Renewal'] > 0) | (grouped['Row_Is_Paid'])].sort_values(
                            'Row_Renewal', ascending=False)

                        if not final_renew.empty:
                            total_income_renew = final_renew['Total_Renewal_Income'].sum()
                            st.metric("💰 กำไรสะสมจากการต่อ", fmt(total_income_renew))

                            st.dataframe(
                                final_renew[['Name', 'Status_Text', 'Total_Renewal_Income']],
                                hide_index=True, use_container_width=True,
                                column_config={
                                    "Name": "ชื่อลูกค้า",
                                    "Status_Text": "สถานะ",
                                    "Total_Renewal_Income": st.column_config.NumberColumn("กำไรสะสม", format="฿%.2f")
                                }
                            )
                        else:
                            st.info("ยังไม่มีข้อมูลการต่อดอก")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")

                # --- ขวา: ค่าปรับ (Penalty - Grouped & Sum) ---
                with c_penalty:
                    st.markdown("##### 💸 ค่าปรับรวม (Total Penalties)")
                    try:
                        # 1. Filter: เอาเฉพาะแถวที่มีค่าปรับ
                        penalty_raw = hist_data[hist_data['Penalty'] > 0]

                        if not penalty_raw.empty:
                            # 2. Group By Name และรวมยอดค่าปรับ
                            penalty_grouped = penalty_raw.groupby('Name')['Penalty'].sum().reset_index()

                            # 3. Sort เรียงจากมากไปน้อย
                            penalty_list = penalty_grouped.sort_values('Penalty', ascending=False)

                            # 4. แสดงผลยอดรวม
                            total_penalty = penalty_list['Penalty'].sum()
                            st.metric("⚠️ ยอดค่าปรับรวมทั้งหมด", fmt(total_penalty))

                            # 5. แสดงตาราง (ชื่อ + ค่าปรับรวม) ไม่มีสถานะ
                            st.dataframe(
                                penalty_list[['Name', 'Penalty']],
                                hide_index=True, use_container_width=True,
                                column_config={
                                    "Name": "ชื่อลูกค้า",
                                    "Penalty": st.column_config.NumberColumn("ค่าปรับรวม", format="฿%.2f")
                                }
                            )
                        else:
                            st.success("✅ ไม่มีใครโดนค่าปรับ")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")

            # =======================================================
            # TAB 4: RAW DATA
            # =======================================================
            with tab4:
                st.subheader("📄 ข้อมูลดิบ (Raw Data)")
                st.dataframe(df)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
    else:
        st.info("กำลังโหลดข้อมูล...")
