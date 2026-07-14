import streamlit as st
import pdfplumber
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Drop Year Planner", layout="wide", page_icon="🎯")

def extract_data_from_pdf(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_rows.extend(table)
        
        if not all_rows:
            return pd.DataFrame()

        # Temporary dataframe
        temp_df = pd.DataFrame(all_rows)
        
        # 1. Asli Heading Dhoondhne ka Logic
        # Hum wo row dhoondhenge jisme 'Date' aur 'Chapter' likha ho
        header_idx = 0
        for i, row in temp_df.iterrows():
            row_str = ' '.join([str(x).lower() for x in row.values])
            if 'date' in row_str and 'chapter' in row_str:
                header_idx = i
                break
        
        # Asli headings set kar rahe hain
        headers = temp_df.iloc[header_idx].apply(lambda x: str(x).replace('\n', ' ').strip() if x else "Unused")
        df = temp_df.iloc[header_idx+1:].reset_index(drop=True)
        df.columns = headers
        
        # Kachra aur repeating headers ko delete karna
        df = df.dropna(how='all')
        df = df[~df.astype(str).apply(lambda x: x.str.contains('Chapter Name|S. No.', case=False)).any(axis=1)]
        df = df.replace(r'\n', ' ', regex=True)
        
        # 2. Source Subject add karna
        subject_name = file.name.rsplit('.', 1)[0]
        df.insert(0, 'Source Subject', subject_name)
        
        # 3. Drop Year Logic (2025 ko 2026 me convert karna)
        # Date wala column dhundo
        date_col = [col for col in df.columns if 'date' in str(col).lower() or 'day' in str(col).lower()]
        if date_col:
            dc = date_col[0]
            # Replace 2025 with 2026 automatically
            df[dc] = df[dc].astype(str).str.replace('2025', '2026', regex=False)
            df.rename(columns={dc: 'Target Date'}, inplace=True)
            
            # Agar PW date format format me 'None' hai toh usko hatao
            df = df[df['Target Date'] != 'None']

        return df

    except Exception as e:
        st.warning(f"Bhai, '{file.name}' me kuch error aaya: {e}")
        return pd.DataFrame()

# UI Layout
st.title("🎯 Drop Year Study Planner")
st.markdown("Tera personal daily schedule. Ek date select kar aur padhai pe focus kar!")

# Sidebar for File Upload
with st.sidebar:
    st.header("Upload PW Planners")
    uploaded_files = st.file_uploader(
        "PDFs yahan drop kar", 
        type="pdf", 
        accept_multiple_files=True
    )

if uploaded_files:
    dataframes = []
    with st.spinner('Data extract ho raha hai, bas ek second...'):
        for file in uploaded_files:
            df = extract_data_from_pdf(file)
            if not df.empty:
                dataframes.append(df)

    if dataframes:
        master_df = pd.concat(dataframes, ignore_index=True)

        # Tabs banate hain main screen ko clean rakhne ke liye
        tab1, tab2 = st.tabs(["📅 Daily View (Focus Mode)", "📊 Master Table (Full Data)"])

        with tab1:
            st.subheader("Tera Aaj Ka Schedule")
            if 'Target Date' in master_df.columns:
                # Sirf valid dates ki list banana
                valid_dates = master_df[master_df['Target Date'].str.strip() != "None"]['Target Date'].dropna().unique().tolist()
                
                # Agar dates hain toh selectbox dikhao
                if valid_dates:
                    selected_date = st.selectbox("Kaunsi date ka schedule dekhna hai?", valid_dates)
                    
                    # Us din ka data filter karo
                    day_df = master_df[master_df['Target Date'] == selected_date]
                    
                    total_lectures = len(day_df)
                    st.success(f"**Bhai, {selected_date} ko tere total {total_lectures} lectures hain!** 🚀")
                    
                    # Har lecture ko ek neat card/box jese dikhana
                    for index, row in day_df.iterrows():
                        sub = row.get('Subject', row.get('Source Subject', 'Unknown'))
                        chap = row.get('Chapter Name', 'N/A')
                        topic = row.get('Topic', row.get('-pic', 'N/A')) # PW uses '-pic' sometimes for Topic
                        lec_no = row.get('Lecture', 'N/A')
                        faculty = row.get('Faculty Name', 'N/A')
                        
                        st.info(f"📚 **{sub}** | 🧑‍🏫 {faculty}")
                        st.markdown(f"**Chapter:** {chap}")
                        st.markdown(f"**Topic (Lec {lec_no}):** {topic}")
                        st.divider()
                else:
                    st.warning("Date format samajh nahi aaya bhai, PDF me dates check kar.")
            else:
                st.warning("Date column nahi mila PDF me.")

        with tab2:
            st.subheader("Pura Master Schedule")
            st.dataframe(master_df, use_container_width=True, hide_index=True)
            
            # Export Option
            csv = master_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Master Planner (CSV)",
                data=csv,
                file_name="Drop_Year_Master_Planner.csv",
                mime="text/csv",
            )
else:
    st.info("👈 Sidebar se apne PDFs upload karna shuru kar aur apna drop year phod de!")