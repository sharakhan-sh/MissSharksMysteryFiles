import os
import streamlit as st
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Miss Shark's Mystery Files",
    page_icon="🔎",
    layout="wide"
)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="shark_user",
        password=os.getenv("DB_PASSWORD"),
        database="miss_shark"
    )

st.title("🔎 Miss Shark's Mystery Files")
st.caption("Detective Case Management System")
st.divider()

page = st.sidebar.radio(
    "Detective Menu",
    ["🏠 Dashboard", "🕵️ Solve a Case", "➕ Add Case",
     "🔍 Search Cases", "⚙️ Manage Cases"]
)

try:
    if page == "🏠 Dashboard":
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM Cases ORDER BY case_id DESC")
        cases = cur.fetchall()
        cur.close()
        conn.close()

        st.subheader("Welcome, Detective!")
        c1, c2 = st.columns(2)
        c1.metric("Total Mystery Cases", len(cases))
        c2.metric("Difficult Cases", sum(
            1 for x in cases
            if (x["difficulty"] or "").lower() == "hard"
        ))

        st.subheader("Case Files")
        for case in cases:
            with st.expander(
                f"#{case['case_id']} — {case['title']} "
                f"({case['difficulty'] or 'Easy'})"
            ):
                st.write(case["description"])
                st.caption(f"Date: {case['case_date'] or 'Not specified'}")

    elif page == "🕵️ Solve a Case":
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT case_id, title, description FROM Cases")
        cases = cur.fetchall()
        cur.close()
        conn.close()

        if cases:
            selected = st.selectbox(
                "Choose a mystery",
                cases,
                format_func=lambda x: f"Case #{x['case_id']}: {x['title']}"
            )
            st.subheader(selected["title"])
            st.write(selected["description"])
            answer = st.text_input("Who or what is your answer?")

            if st.button("Submit Answer"):
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(
                    "SELECT answer FROM Cases WHERE case_id=%s",
                    (selected["case_id"],)
                )
                result = cur.fetchone()
                cur.close()
                conn.close()

                if result and answer.strip().casefold() == result[0].strip().casefold():
                    st.success("Correct! Mystery solved, Detective! 🎉")
                else:
                    st.error("Not quite! Investigate the clues again.")
        else:
            st.info("No cases have been added yet.")

    elif page == "➕ Add Case":
        st.subheader("Create a New Mystery")
        with st.form("add_case"):
            title = st.text_input("Case title")
            description = st.text_area("Case description")
            answer = st.text_input("Correct answer")
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            case_date = st.date_input("Case date")
            submitted = st.form_submit_button("Save Case")

        if submitted:
            if title.strip() and description.strip() and answer.strip():
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO Cases
                    (title, description, answer, difficulty, case_date)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (title, description, answer, difficulty, str(case_date))
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("New case saved!")
            else:
                st.warning("Please complete all fields.")

    elif page == "🔍 Search Cases":
        query = st.text_input("Search by case title")
        if query:
            conn = connect_db()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM Cases WHERE title LIKE %s",
                (f"%{query}%",)
            )
            results = cur.fetchall()
            cur.close()
            conn.close()

            if results:
                for case in results:
                    st.subheader(case["title"])
                    st.write(case["description"])
                    st.caption(f"Case #{case['case_id']} · {case['difficulty']}")
            else:
                st.info("No matching cases found.")

    elif page == "⚙️ Manage Cases":
        st.subheader("Update or Delete Case Records")
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM Cases ORDER BY case_id")
        cases = cur.fetchall()
        cur.close()
        conn.close()

        if cases:
            selected = st.selectbox(
                "Select a case",
                cases,
                format_func=lambda x: f"#{x['case_id']} — {x['title']}"
            )

            with st.form("update_case"):
                new_title = st.text_input("Title", selected["title"])
                new_description = st.text_area(
                    "Description", selected["description"]
                )
                new_answer = st.text_input("Answer", selected["answer"])
                new_difficulty = st.selectbox(
                    "Difficulty", ["Easy", "Medium", "Hard"],
                    index=["Easy", "Medium", "Hard"].index(
                        selected["difficulty"]
                        if selected["difficulty"] in ["Easy", "Medium", "Hard"]
                        else "Easy"
                    )
                )
                update = st.form_submit_button("Update Case")

            if update:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(
                    """UPDATE Cases SET title=%s, description=%s,
                    answer=%s, difficulty=%s WHERE case_id=%s""",
                    (new_title, new_description, new_answer,
                     new_difficulty, selected["case_id"])
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Case updated. Refresh the page to see changes.")

            if st.button("Delete Selected Case"):
                conn = connect_db()
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM Cases WHERE case_id=%s",
                    (selected["case_id"],)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Case deleted. Refresh the page.")
        else:
            st.info("There are no cases to manage.")

except mysql.connector.Error as e:
    st.error(f"Database connection error: {e}")
    st.info("Check that MySQL is running and your database credentials are correct.")
