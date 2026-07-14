import streamlit as st
import pdfplumber
import pandas as pd
import random
import time

# Page Configuration
st.set_page_config(page_title="Master Study Planner", layout="wide", page_icon="🎯")

# Motivational Quotes List
QUOTES = [
    "Push harder than yesterday if you want a different tomorrow.",
    "Discipline is choosing between what you want now and what you want most.",
    "Your future is created by what you do today, not tomorrow.",
    "Success is the sum of small efforts, repeated day in and day out.",
    "Don't stop when you're tired. Stop when you're done.",
    "A year from now, you will wish you had started today."
]

# Typewriter effect generator
def stream_quote():
    quote = random.choice(QUOTES)
    for word in quote.split(" "):
        yield word + " "
        time.sleep(0.05)

def extract_data_from_pdf(file, orig_year, target_year):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_rows.extend(table)
        
        if not all_rows:
            return pd.DataFrame()

        temp_df = pd.DataFrame(all_rows)
        
        # Find real headers
        header_idx = 0
        for i, row in temp_df.iterrows():
            row_str = ' '.join([str(x).lower() for x in row.values])
            if 'date' in row_str and 'chapter' in row_str:
                header_idx = i
                break
        
        headers = temp_df.iloc[header_idx].apply(lambda x: str(x).replace('\n', ' ').strip() if x else "Unused")
        df = temp_df.iloc[header_idx+1:].reset_index(drop=True)
        df.columns = headers
        
        # Clean dataframe
        df = df.dropna(how='all')
        df = df[~df.astype(str).apply(lambda x: x.str.contains('Chapter Name|S. No.', case=False)).any(axis=1)]
        df = df.replace(r'\n', ' ', regex=True)
        
        # Insert Source Subject
        subject_name = file.name.rsplit('.', 1)[0]
        df.insert(0, 'Source Subject', subject_name)
        
        # Dynamic Year Conversion
        date_col = [col for col in df.columns if 'date' in str(col).lower() or 'day' in str(col).lower()]
        if date_col:
            dc = date_col[0]
            df[dc] = df[dc].astype(str).str.replace(orig_year, target_year, regex=False)
            df.rename(columns={dc: 'Target Date'}, inplace=True)
            df = df[df['Target Date'] != 'None']

        return df

    except Exception as e:
        st.warning(f"Error parsing '{file.name}': {e}")
        return pd.DataFrame()

# Main UI Layout
st.title("🎯 Daily Execution Planner")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("1. Year Conversion")
    col1, col2 = st.columns(2)
    with col1:
        original_year = st.text_input("Original Year", value="2025")
    with col2:
        new_year = st.text_input("Target Year", value="2026")
        
    st.subheader("2. Upload Planners")
    uploaded_files = st.file_uploader(
        "Upload PDF Schedules", 
        type="pdf", 
        accept_multiple_files=True
    )

# Logic execution
if not uploaded_files:
    # Typewriter Motivation
    st.info("💡 Daily Motivation")
    st.write_stream(stream_quote)
    
    st.divider()
    
    # Steps
    st.subheader("How to Use This Tracker:")
    st.markdown("""
    **Step 1:** Look at your PDF planner and identify the year written in the dates (e.g., 2025). Enter it in the **Original Year** box in the sidebar.  
    **Step 2:** Enter the year you actually want to study in the **Target Year** box (e.g., 2026 for a drop year).  
    **Step 3:** Upload one or multiple class schedules/planners in PDF format using the sidebar uploader.  
    **Step 4:** Navigate to the **Daily View** tab, select today's date, and start executing your lectures!
    """)
else:
    dataframes = []
    with st.spinner('Extracting schedule data...'):
        for file in uploaded_files:
            df = extract_data_from_pdf(file, original_year, new_year)
            if not df.empty:
                dataframes.append(df)

    if dataframes:
        master_df = pd.concat(dataframes, ignore_index=True)

        tab1, tab2 = st.tabs(["📅 Daily View (Focus Mode)", "📊 Master Table (Full Data)"])

        with tab1:
            st.subheader("Your Schedule for the Day")
            if 'Target Date' in master_df.columns:
                valid_dates = master_df[master_df['Target Date'].str.strip() != "None"]['Target Date'].dropna().unique().tolist()
                
                if valid_dates:
                    selected_date = st.selectbox("Select Date:", valid_dates)
                    day_df = master_df[master_df['Target Date'] == selected_date]
                    total_lectures = len(day_df)
                    
                    st.success(f"**Target for {selected_date}: {total_lectures} lectures scheduled.** 🚀")
                    
                    for index, row in day_df.iterrows():
                        sub = row.get('Subject', row.get('Source Subject', 'Unknown'))
                        chap = row.get('Chapter Name', 'N/A')
                        topic = row.get('Topic', row.get('-pic', 'N/A')) 
                        lec_no = row.get('Lecture', 'N/A')
                        faculty = row.get('Faculty Name', 'N/A')
                        
                        st.info(f"📚 **{sub}** | 🧑‍🏫 {faculty}")
                        st.markdown(f"**Chapter:** {chap}")
                        st.markdown(f"**Topic (Lec {lec_no}):** {topic}")
                        st.divider()
                else:
                    st.warning("Could not identify valid dates. Please check PDF format.")
            else:
                st.warning("Date column not found in the uploaded PDFs.")

        with tab2:
            st.subheader("Complete Master Schedule")
            st.dataframe(master_df, use_container_width=True, hide_index=True)
            
            csv = master_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Master Planner (CSV)",
                data=csv,
                file_name="Master_Planner.csv",
                mime="text/csv",
            )
