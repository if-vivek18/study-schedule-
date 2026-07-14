# 🎯 Daily Execution Planner

A clean, distraction-free study schedule tracker built with Streamlit and Python. This app is specifically designed for students (especially drop-year students) to convert complex PDF batch schedules (like Physics Wallah planners) into an easy-to-use daily focus dashboard.

## ✨ Features
* **📄 Automated PDF Parsing:** Uses `pdfplumber` to accurately extract tables from study planner PDFs without messing up the row/column structure.
* **⏳ Dynamic Year Conversion:** Automatically updates the schedule year (e.g., converting 2025 schedules to 2026 for drop-year students).
* **📅 Daily Focus Mode:** A clutter-free UI that shows exactly how many lectures you have for the selected day, along with subject, chapter, topic, and faculty details.
* **📊 Master Table & Export:** View your entire merged schedule across all subjects and download it as a CSV file.
* **💡 Motivational Typewriter:** Get a random motivational quote every time you open the app to stay disciplined
