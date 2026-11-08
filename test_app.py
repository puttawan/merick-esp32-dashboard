# Project: Merickpolymer2026esp32
# Version: V10.1 (Incremented by +0.1 from V10.0)
# Description: Real-time ESP32 Dashboard with Fixed Normal Mode Production Column Variables (p1-p4)

import streamlit as st
import gspread
import math
from datetime import date, datetime
from google.oauth2.service_account import Credentials

# Configure web page settings
st.set_page_config(
    page_title="Merick ESP32 Dashboard V10.1",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Spreadsheet configuration
SPREADSHEET_ID = "1dHnIRc0VDO4eM-mihbQZeC25rUY47Yo8MlUSqV5z-E8"
SHEET_NAME = "Sheet1"

# Service account authorization scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Top Layout Controls
head_col1, head_col2, head_col3 = st.columns([2.5, 1.2, 1.3])
with head_col1:
    st.title("🏭 Merick ESP32 Monitor (V10.1)")
with head_col2:
    view_mode = st.radio(
        "รูปแบบหน้าจอ",
        options=["ปกติ (Normal)", "Present A4"],
        horizontal=True,
        index=0
    )
with head_col3:
    selected_date = st.date_input(
        "คลิก เลือกวันที่",
        value=date.today(),
        key="calendar_date_picker"
    )

is_present = (view_mode == "Present A4")

# Sidebar Configuration
st.sidebar.title("⚙️ การตั้งค่าระบบ")
st.sidebar.markdown("**Version:** `V10.1`")
refresh_interval = st.sidebar.selectbox(
    "ความถี่ในการอัปเดตข้อมูล (วินาที)",
    options=[5, 10, 15, 30, 60],
    index=1
)
st.sidebar.caption("ข้อมูลและกราฟทุกตัวแสดงผลตามวันที่เลือก")

# Dynamic CSS Styling
css_present_strict = """
/* Present mode: Hide sidebar and fit single canvas */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    display: none !important;
}
html, body, [data-testid="stAppViewContainer"] {
    overflow-y: hidden !important;
}
.main .block-container {
    max-width: 100% !important;
    padding-top: 8px !important;
    padding-bottom: 6px !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
}
h1 {
    font-size: 20px !important;
    margin: 0 !important;
    padding: 0 !important;
}
h3 {
    font-size: 13px !important;
    margin: 2px 0 !important;
    padding: 0 !important;
}
hr {
    margin: 4px 0 !important;
    padding: 0 !important;
}
div[data-testid="stMetric"] {
    padding: 4px 8px !important;
    background-color: #1a1f2c !important;
    border: 1px solid #2e384d !important;
    border-radius: 6px !important;
}
div[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    margin: 0 !important;
}
div[data-testid="stMetricValue"] div {
    font-size: 16px !important;
    font-weight: 700 !important;
}
""" if is_present else """
.main .block-container {
    padding-top: 25px !important;
    padding-bottom: 25px !important;
}
"""

st.markdown(
    f"""<style>
/* Main App Dark Background */
.stApp {{
background-color: #0e1117;
color: #ffffff !important;
}}

/* Sidebar Dark Theme */
section[data-testid="stSidebar"] {{
background-color: #111827 !important;
border-right: 1px solid #2e384d !important;
}}
section[data-testid="stSidebar"] * {{
color: #ffffff !important;
}}

/* Fix Version Tag */
section[data-testid="stSidebar"] code {{
background-color: #1e293b !important;
color: #38bdf8 !important;
font-weight: 700 !important;
padding: 2px 8px !important;
border-radius: 4px !important;
border: 1px solid #38bdf8 !important;
}}

/* Fix Selectbox Input Box and Dropdown Text */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div {{
background-color: #1e293b !important;
border: 1px solid #475569 !important;
border-radius: 6px !important;
}}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] * {{
background-color: transparent !important;
color: #ffffff !important;
font-weight: 700 !important;
font-size: 15px !important;
}}
section[data-testid="stSidebar"] svg {{
fill: #ffffff !important;
}}

/* Force Bright White on Main Page */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6, .main label {{
color: #ffffff !important;
}}

/* Radio Selector on Top Header */
div[data-testid="stRadio"] label p {{
font-size: 13px !important;
font-weight: 600 !important;
color: #ffffff !important;
}}

/* Calendar Date Picker Styling - 18px Font */
div[data-testid="stDateInput"] label p {{
font-size: 15px !important;
font-weight: 600 !important;
color: #ffffff !important;
}}
div[data-testid="stDateInput"] input {{
font-size: 18px !important;
font-weight: 700 !important;
color: #ffffff !important;
height: 38px !important;
}}
div[data-testid="stDateInput"] {{
background-color: #1a1f2c;
border: 1px solid #2e384d;
padding: 2px 8px;
border-radius: 6px;
}}

/* Machine Status Alert Box */
div[data-testid="stAlert"] {{
background-color: #f1f5f9 !important;
border-radius: 6px !important;
border: 2px solid #94a3b8 !important;
padding: 5px 14px !important;
}}
div[data-testid="stAlert"] * {{
color: #000000 !important;
font-weight: 700 !important;
font-size: 15px !important;
}}

/* Metric Cards Default */
div[data-testid="stMetric"] {{
background-color: #1a1f2c;
border: 1px solid #2e384d;
padding: 10px;
border-radius: 8px;
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}}
div[data-testid="stMetricLabel"] p {{
color: #ffffff !important;
font-weight: 600 !important;
font-size: 13px !important;
}}
div[data-testid="stMetricLabel"] {{
color: #ffffff !important;
}}
div[data-testid="stMetricValue"] div {{
color: #ffffff !important;
font-weight: 700 !important;
font-size: 22px !important;
}}
div[data-testid="stMetricValue"] {{
color: #ffffff !important;
}}

{css_present_strict}
</style>""",
    unsafe_allow_html=True
)

# Parse time string into total seconds from midnight
def parse_time_seconds(time_str):
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
        elif len(parts) == 2:
            return int(parts[0]) * 3600 + int(parts[1]) * 60
    except Exception:
        pass
    return 0

# Match row timestamp with selected calendar date
def is_matching_date(timestamp_str, target_date):
    if not timestamp_str:
        return False
    clean_ts = timestamp_str.strip().split()[0]
    formats = [
        target_date.strftime("%d/%m/%Y"),
        target_date.strftime("%Y-%m-%d"),
        f"{target_date.day}/{target_date.month}/{target_date.year}",
        f"{target_date.month}/{target_date.day}/{target_date.year}"
    ]
    return any(clean_ts == fmt or clean_ts.startswith(fmt) for fmt in formats)

# Fetch and sort rows chronologically from day start to end
def fetch_sorted_timeline_data(target_date):
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    all_values = sheet.get_all_values()
    
    headers = all_values[0] if len(all_values) > 0 else []
    
    time_idx = 0
    curr_idx = headers.index("Current") if "Current" in headers else -1
    count_a_idx = headers.index("CountA") if "CountA" in headers else -1
    
    matched_rows = []
    for r in all_values[1:]:
        if len(r) > time_idx and is_matching_date(r[time_idx], target_date):
            raw_t = r[time_idx].strip()
            t_str = raw_t.split()[-1] if " " in raw_t else raw_t
            sec = parse_time_seconds(t_str)
            matched_rows.append((sec, t_str, r))
            
    has_data = len(matched_rows) > 0
    
    if has_data:
        matched_rows.sort(key=lambda item: item[0])
        display_records = matched_rows
    else:
        fallback_r = all_values[3] if len(all_values) >= 4 else (all_values[1] if len(all_values) > 1 else [])
        raw_t = fallback_r[time_idx].strip() if len(fallback_r) > time_idx else "00:00:00"
        t_str = raw_t.split()[-1] if " " in raw_t else raw_t
        display_records = [(parse_time_seconds(t_str), t_str, fallback_r)]
        
    snapshot_row = display_records[-1][2]
    snapshot_data = dict(zip(headers, snapshot_row))
    
    time_labels = []
    time_secs = []
    count_a_list = []
    current_list = []
    
    for sec, t_str, r in display_records:
        time_labels.append(t_str)
        time_secs.append(sec)
        
        try:
            val_c = float(r[count_a_idx]) if (count_a_idx != -1 and len(r) > count_a_idx and r[count_a_idx] != "") else 0.0
        except ValueError:
            val_c = 0.0
        count_a_list.append(val_c)
        
        try:
            val_i = float(r[curr_idx]) if (curr_idx != -1 and len(r) > curr_idx and r[curr_idx] != "") else 0.0
        except ValueError:
            val_i = 0.0
        current_list.append(val_i)
        
    history = {
        "time_labels": time_labels,
        "time_secs": time_secs,
        "count_a": count_a_list,
        "current": current_list,
        "has_data": has_data,
        "record_count": len(matched_rows)
    }
    
    return snapshot_data, history

# Render 4-zone semi-circle gauge
def render_four_zone_gauge(label, value, compact=False):
    val = max(min(float(value), 100.0), 0.0)
    angle_deg = 180.0 - (val / 100.0 * 180.0)
    angle_rad = math.radians(angle_deg)
    
    cx = 100.0
    cy = 82.0 if compact else 88.0
    needle_r = 46.0 if compact else 50.0
    nx = cx + needle_r * math.cos(angle_rad)
    ny = cy - needle_r * math.sin(angle_rad)
    
    height_svg = 88 if compact else 105
    pad_box = "6px 8px" if compact else "10px"
    
    svg = f"""<div style="background-color: #1a1f2c; border: 1px solid #2e384d; border-radius: 6px; padding: {pad_box}; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
<p style="margin: 0; color: #ffffff; font-size: 12px; font-weight: 600;">{label}</p>
<svg viewBox="0 0 200 110" width="100%" height="{height_svg}">
<path d="M 30 82 A 70 70 0 0 1 170 82" fill="none" stroke="#ef4444" stroke-width="11" stroke-dasharray="88 220" stroke-dashoffset="0" />
<path d="M 30 82 A 70 70 0 0 1 170 82" fill="none" stroke="#f97316" stroke-width="11" stroke-dasharray="55 220" stroke-dashoffset="-88" />
<path d="M 30 82 A 70 70 0 0 1 170 82" fill="none" stroke="#eab308" stroke-width="11" stroke-dasharray="44 220" stroke-dashoffset="-143" />
<path d="M 30 82 A 70 70 0 0 1 170 82" fill="none" stroke="#22c55e" stroke-width="11" stroke-dasharray="33 220" stroke-dashoffset="-187" />
<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />
<circle cx="{cx}" cy="{cy}" r="5" fill="#ffffff" />
<circle cx="{cx}" cy="{cy}" r="2" fill="#1a1f2c" />
<text x="{cx}" y="{cy + 20}" text-anchor="middle" font-size="16" font-weight="bold" fill="#ffffff">{val:.1f}%</text>
</svg>
<div style="display: flex; justify-content: space-between; font-size: 9px; font-weight: bold; padding: 0 10px;">
<span style="color: #ef4444;">0%</span>
<span style="color: #f97316;">40%</span>
<span style="color: #eab308;">65%</span>
<span style="color: #22c55e;">85%</span>
<span style="color: #22c55e;">100%</span>
</div>
</div>"""
    st.markdown(svg, unsafe_allow_html=True)

# Render chronological timeline area chart with custom formatting and font options
def render_day_timeline_chart(title, subtitle, history_vals, time_labels, time_secs, unit, color_line, color_fill, is_cumulative=False, compact=False, custom_val_font=None, is_integer_format=False):
    if not history_vals:
        return
    max_val = max(history_vals)
    min_val = min(history_vals)
    cur_val = history_vals[-1]
    
    t_start = time_labels[0] if len(time_labels) > 0 else "--:--:--"
    t_end = time_labels[-1] if len(time_labels) > 0 else "--:--:--"
    
    width = 400
    height = 115 if compact else 130
    pad_x = 18
    pad_y = 18 if compact else 22
    
    range_val = max_val - min_val if max_val != min_val else (1.0 if max_val == 0 else max_val)
    
    t_min_sec = time_secs[0] if len(time_secs) > 0 else 0
    t_max_sec = time_secs[-1] if len(time_secs) > 0 else 1
    t_range_sec = t_max_sec - t_min_sec if t_max_sec > t_min_sec else 1
    
    points = []
    n = len(history_vals)
    for i in range(n):
        val = history_vals[i]
        sec = time_secs[i]
        
        if t_range_sec > 1:
            x = pad_x + ((sec - t_min_sec) / t_range_sec) * (width - 2 * pad_x)
        else:
            step = (width - 2 * pad_x) / (n - 1) if n > 1 else 0
            x = pad_x + i * step
            
        y = (height - pad_y) - ((val - min_val) / range_val) * (height - 2 * pad_y)
        points.append((x, y))
        
    line_path = "M " + " L ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in points])
    area_path = f"{line_path} L {points[-1][0]:.1f},{height - pad_y} L {points[0][0]:.1f},{height - pad_y} Z"
    
    grad_id = f"grad_{title.replace(' ', '')}"
    diff_val = history_vals[-1] - history_vals[0]
    
    if is_integer_format:
        sub_info = f"{subtitle} (+{int(round(diff_val)):,} {unit})" if is_cumulative else subtitle
        cur_val_str = f"{int(round(cur_val)):,}"
        max_val_str = f"{int(round(max_val)):,}"
    else:
        sub_info = f"{subtitle} (+{diff_val:.1f} {unit})" if is_cumulative else subtitle
        cur_val_str = f"{cur_val:.2f}"
        max_val_str = f"{max_val:.2f}"
    
    pad_box = "8px 12px" if compact else "10px 14px"
    font_val = custom_val_font if custom_val_font else ("18px" if compact else "22px")
    
    svg = f"""<div style="background-color: #1a1f2c; border: 1px solid #2e384d; border-radius: 6px; padding: {pad_box}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 2px;">
<span style="font-size: 13px; font-weight: 600; color: #ffffff;">{title}</span>
<span style="font-size: 11px; font-weight: bold; color: #f59e0b; background-color: rgba(245, 158, 11, 0.15); padding: 1px 6px; border-radius: 3px; border: 1px solid #f59e0b;">
MAX: {max_val_str} {unit}
</span>
</div>
<p style="margin: 0; font-size: 10px; color: #94a3b8;">{sub_info}</p>
<div style="font-size: {font_val}; font-weight: bold; color: {color_line}; margin-bottom: 2px;">
{cur_val_str} <span style="font-size: 13px; color: #94a3b8;">{unit}</span>
</div>
<svg viewBox="0 0 {width} {height}" width="100%" height="{height}">
<defs>
<linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="{color_fill}" stop-opacity="0.6"/>
<stop offset="100%" stop-color="{color_fill}" stop-opacity="0.05"/>
</linearGradient>
</defs>
<line x1="{pad_x}" y1="{height - pad_y}" x2="{width - pad_x}" y2="{height - pad_y}" stroke="#475569" stroke-width="1.5"/>
<line x1="{pad_x}" y1="{height - pad_y}" x2="{pad_x}" y2="{height - pad_y + 4}" stroke="#475569" stroke-width="1.5"/>
<line x1="{width - pad_x}" y1="{height - pad_y}" x2="{width - pad_x}" y2="{height - pad_y + 4}" stroke="#475569" stroke-width="1.5"/>
<path d="{area_path}" fill="url(#{grad_id})" />
<path d="{line_path}" fill="none" stroke="{color_line}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
<circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="3.5" fill="{color_line}" />
<text x="{pad_x}" y="{height - 2}" font-size="10" fill="#94a3b8" text-anchor="start">เริ่ม: {t_start}</text>
<text x="{width - pad_x}" y="{height - 2}" font-size="10" fill="#94a3b8" text-anchor="end">สิ้นสุด: {t_end}</text>
</svg>
</div>"""
    st.markdown(svg, unsafe_allow_html=True)

# Helper function to render Temperature Bar Chart
def render_temp_bars(t1, t2, t3, t4, compact=False):
    max_temp = max(max(t1, t2, t3, t4, 1.0), 100.0)
    pad = "8px 12px" if compact else "15px 20px"
    bar_h = 10 if compact else 16
    font_s = 11 if compact else 13
    mb = 4 if compact else 8
    
    svg = f"""<div style="background-color: #1a1f2c; padding: {pad}; border-radius: 8px; border: 1px solid #2e384d;">
<p style="margin: 0 0 4px 0; color: #ffffff !important; font-size: {font_s}px; font-weight: bold;">อุณหภูมิ (°C)</p>
<div style="margin-bottom: {mb}px;">
<span style="display:inline-block; width: 22px; font-size: {font_s}px; color: #ffffff;">T1</span>
<div style="display:inline-block; width: {(t1/max_temp)*65}%; background-color: #f97316; height: {bar_h}px; border-radius: 3px;"></div>
<span style="margin-left: 6px; font-size: {font_s}px; color: #ffffff;">{t1:.1f}</span>
</div>
<div style="margin-bottom: {mb}px;">
<span style="display:inline-block; width: 22px; font-size: {font_s}px; color: #ffffff;">T2</span>
<div style="display:inline-block; width: {(t2/max_temp)*65}%; background-color: #ef4444; height: {bar_h}px; border-radius: 3px;"></div>
<span style="margin-left: 6px; font-size: {font_s}px; color: #ffffff;">{t2:.1f}</span>
</div>
<div style="margin-bottom: {mb}px;">
<span style="display:inline-block; width: 22px; font-size: {font_s}px; color: #ffffff;">T3</span>
<div style="display:inline-block; width: {(t3/max_temp)*65}%; background-color: #06b6d4; height: {bar_h}px; border-radius: 3px;"></div>
<span style="margin-left: 6px; font-size: {font_s}px; color: #ffffff;">{t3:.1f}</span>
</div>
<div>
<span style="display:inline-block; width: 22px; font-size: {font_s}px; color: #ffffff;">T4</span>
<div style="display:inline-block; width: {(t4/max_temp)*65}%; background-color: #3b82f6; height: {bar_h}px; border-radius: 3px;"></div>
<span style="margin-left: 6px; font-size: {font_s}px; color: #ffffff;">{t4:.1f}</span>
</div>
</div>"""
    st.markdown(svg, unsafe_allow_html=True)

# Fragment execution for auto-refreshing dashboard
@st.fragment(run_every=refresh_interval)
def display_dashboard():
    try:
        data, history = fetch_sorted_timeline_data(selected_date)
        machine_status = str(data.get("MachineStatus", "UNKNOWN")).strip().upper()

        if not history["has_data"] and not is_present:
            st.warning(f"⚠️ ไม่พบข้อมูลของวันที่ {selected_date.strftime('%d/%m/%Y')} ในชีต — แสดงข้อมูลแถวที่ 4 แทน")

        # Machine Status Banner
        if machine_status in ["RUN", "RUNNING"]:
            st.success(f"🟢 MACHINE STATUS: {machine_status} (เครื่องจักรกำลังทำงานปกติ)")
        elif machine_status in ["STANDBY", "IDLE"]:
            st.warning(f"🟡 MACHINE STATUS: {machine_status} (เครื่องจักรกำลังสแตนด์บาย)")
        elif machine_status in ["STOP", "ALARM", "DOWN", "ERROR"]:
            st.error(f"🔴 MACHINE STATUS: {machine_status} (เครื่องจักรหยุดทำงานหรือมีสัญญาณเตือน)")
        else:
            st.info(f"⚪ MACHINE STATUS: {machine_status}")

        if not is_present:
            st.caption(f"🕒 ข้อมูลเวลา: {data.get('Timestamp', '-')} | อัปเดตทุกๆ {refresh_interval} วินาที")
            st.divider()

        # Extract numerical metrics
        oee_val = float(data.get('CalcOEE', 0) or 0)
        avail_val = float(data.get('CalcAvail', 0) or 0)
        perf_val = float(data.get('CalcPerf', 0) or 0)
        qual_val = float(data.get('CalcQual', 0) or 0)

        t1 = float(data.get('T1', 0) or 0)
        t2 = float(data.get('T2', 0) or 0)
        t3 = float(data.get('T3', 0) or 0)
        t4 = float(data.get('T4', 0) or 0)

        # Dynamic CountA Font Size: Normal = 36px, Present A4 = 32px
        count_a_font = "32px" if is_present else "36px"

        # Format CountA card value as integer with comma separation
        try:
            count_a_raw = float(data.get('CountA', 0) or 0)
            count_a_formatted = f"{int(round(count_a_raw)):,}"
        except Exception:
            count_a_formatted = str(data.get('CountA', '-'))

        if is_present:
            # === PRESENT MODE A4: RESTORED TOP METRICS + COUNTA (32px, NO DECIMALS, COMMA SEPARATED) ===
            # Step 1: Top Metric Cards for OEE, Avail, Perf, Qual
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("OEE", f"{oee_val:.1f}%")
            m2.metric("Availability (A)", f"{avail_val:.1f}%")
            m3.metric("Performance (P)", f"{perf_val:.1f}%")
            m4.metric("Quality (Q)", f"{qual_val:.1f}%")

            # Step 2: 4-Zone Gauges directly below the cards
            g1, g2, g3, g4 = st.columns(4)
            with g1:
                render_four_zone_gauge("OEE", oee_val, compact=True)
            with g2:
                render_four_zone_gauge("Availability", avail_val, compact=True)
            with g3:
                render_four_zone_gauge("Performance", perf_val, compact=True)
            with g4:
                render_four_zone_gauge("Quality", qual_val, compact=True)

            # Step 3: Time-Series Area Charts (CountA: 32px, integer with commas)
            c_left, c_right = st.columns(2)
            with c_left:
                render_day_timeline_chart(
                    "Count A Progression",
                    "ยอดการนับชิ้นงานจากเริ่มต้นจนถึงสิ้นสุดวัน",
                    history["count_a"],
                    history["time_labels"],
                    history["time_secs"],
                    "pcs",
                    "#38bdf8",
                    "#38bdf8",
                    is_cumulative=True,
                    compact=True,
                    custom_val_font=count_a_font,
                    is_integer_format=True
                )
            with c_right:
                render_day_timeline_chart(
                    "Current Machine On/Off",
                    "ระดับกระแสไฟฟ้าขณะเปิด-ปิดเครื่อง",
                    history["current"],
                    history["time_labels"],
                    history["time_secs"],
                    "A",
                    "#10b981",
                    "#10b981",
                    is_cumulative=False,
                    compact=True,
                    is_integer_format=False
                )

            # Step 4: Floor Metrics (CountA Card: 32px, integer with commas)
            b1, b2, b3 = st.columns([1.5, 1.5, 1.2])
            with b1:
                st.markdown("### 📦 การผลิต")
                p1, p2, p3, p4 = st.columns(4)
                with p1:
                    st.markdown(
                        f"""<div style="background-color: #1a1f2c; border: 1px solid #2e384d; border-radius: 6px; padding: 4px 8px;">
<p style="margin: 0; font-size: 11px; color: #ffffff; font-weight: 600;">Count A</p>
<div style="font-size: {count_a_font}; font-weight: 700; color: #ffffff; line-height: 1.1;">{count_a_formatted}</div>
</div>""",
                        unsafe_allow_html=True
                    )
                p2.metric("Count B", data.get("CountB", "-"))
                p3.metric("Defects", data.get("ManualDefect", "-"))
                p4.metric("CRatio", data.get("CRatio", "-"))

            with b2:
                st.markdown("### ⚡ ระบบไฟฟ้า")
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Volt", f"{data.get('Voltage', '-')}V")
                e2.metric("Amp", f"{data.get('Current', '-')}A")
                e3.metric("Watt", f"{data.get('Power', '-')}W")
                e4.metric("PF", data.get("PF", "-"))

            with b3:
                render_temp_bars(t1, t2, t3, t4, compact=True)

        else:
            # === NORMAL MODE: STANDARD SCROLLABLE VIEW (CountA: 36px, NO DECIMALS, COMMA SEPARATED) ===
            st.markdown("### 📈 OEE Overview & 4-Zone Gauges")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("OEE", f"{oee_val:.1f}%")
            m2.metric("Availability (A)", f"{avail_val:.1f}%")
            m3.metric("Performance (P)", f"{perf_val:.1f}%")
            m4.metric("Quality (Q)", f"{qual_val:.1f}%")

            g1, g2, g3, g4 = st.columns(4)
            with g1:
                render_four_zone_gauge("OEE", oee_val, compact=False)
            with g2:
                render_four_zone_gauge("Availability", avail_val, compact=False)
            with g3:
                render_four_zone_gauge("Performance", perf_val, compact=False)
            with g4:
                render_four_zone_gauge("Quality", qual_val, compact=False)

            st.divider()

            st.markdown(f"### 📊 กราฟแนวโน้มแสดงระดับเส้นจากเวลาเริ่มต้นถึงสิ้นสุดของวัน (Col A)")
            col_c_a, col_curr = st.columns(2)
            with col_c_a:
                render_day_timeline_chart(
                    "Count A Progression",
                    "ยอดการนับชิ้นงานจากเริ่มต้นจนถึงสิ้นสุดวัน",
                    history["count_a"],
                    history["time_labels"],
                    history["time_secs"],
                    "pcs",
                    "#38bdf8",
                    "#38bdf8",
                    is_cumulative=True,
                    compact=False,
                    custom_val_font=count_a_font,
                    is_integer_format=True
                )
            with col_curr:
                render_day_timeline_chart(
                    "Current Machine On/Off",
                    "ระดับกระแสไฟฟ้าขณะเปิด-ปิดเครื่องจากเริ่มต้นจนถึงสิ้นสุดวัน",
                    history["current"],
                    history["time_labels"],
                    history["time_secs"],
                    "A",
                    "#10b981",
                    "#10b981",
                    is_cumulative=False,
                    compact=False,
                    is_integer_format=False
                )

            st.divider()

            st.markdown(f"### 🌡️ อุณหภูมิเซนเซอร์ (°C) ประจำวันที่ {selected_date.strftime('%d/%m/%Y')}")
            t_cols = st.columns(4)
            t_cols[0].metric("T1", f"{t1:.1f} °C")
            t_cols[1].metric("T2", f"{t2:.1f} °C")
            t_cols[2].metric("T3", f"{t3:.1f} °C")
            t_cols[3].metric("T4", f"{t4:.1f} °C")

            render_temp_bars(t1, t2, t3, t4, compact=False)

            st.divider()

            col_elec, col_prod = st.columns(2)
            with col_elec:
                st.markdown(f"### ⚡ ระบบไฟฟ้าและพลังงาน ประจำวันที่ {selected_date.strftime('%d/%m/%Y')}")
                e1, e2 = st.columns(2)
                e1.metric("Voltage", f"{data.get('Voltage', '-')} V")
                e2.metric("Current", f"{data.get('Current', '-')} A")
                e3, e4 = st.columns(2)
                e3.metric("Power", f"{data.get('Power', '-')} W")
                e4.metric("Power Factor", data.get("PF", "-"))

            with col_prod:
                st.markdown(f"### 📦 ยอดการผลิตและของเสีย ประจำวันที่ {selected_date.strftime('%d/%m/%Y')}")
                p1, p2 = st.columns(2)
                with p1:
                    st.markdown(
                        f"""<div style="background-color: #1a1f2c; border: 1px solid #2e384d; border-radius: 8px; padding: 10px;">
<p style="margin: 0; font-size: 13px; color: #ffffff; font-weight: 600;">Count A</p>
<div style="font-size: {count_a_font}; font-weight: 700; color: #ffffff; line-height: 1.1;">{count_a_formatted}</div>
</div>""",
                        unsafe_allow_html=True
                    )
                p2.metric("Count B", data.get("CountB", "-"))
                p3, p4 = st.columns(2)
                p3.metric("Defects (ชิ้นงานเสีย)", data.get("ManualDefect", "-"))
                p4.metric("Cycle Ratio", data.get("CRatio", "-"))

    except Exception as err:
        st.error(f"เกิดข้อผิดพลาดในการอ่านข้อมูล: {err}")

# Execute dashboard logic
display_dashboard()