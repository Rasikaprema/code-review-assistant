import streamlit as st
import os
import requests
import difflib
import streamlit.components.v1 as components

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Code Review Assistant",
    page_icon="🛠️",
    layout="wide"
)

# =====================================
# 🔐 LOGIN SWITCH (TURN ON/OFF LOGIN)
# =====================================
ENABLE_LOGIN = False   # 👉 change to False to disable login completely

# If login disabled → skip everything
if not ENABLE_LOGIN:
    pass  # Continue loading app normally

else:
    # Read credentials from environment variables
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")

    # Warning if credentials not set—but do not block the app
    if not USERNAME or not PASSWORD:
        st.warning("⚠️ Login enabled but APP_USERNAME or APP_PASSWORD not set.")
        USERNAME = PASSWORD = None  # avoids false login match

    # Session state to track login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If not logged in → show login screen
    if not st.session_state.logged_in:
        st.title("🔐 Secure Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if USERNAME and PASSWORD and username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password")

        st.stop()  # Stop app from loading until logged in


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<style>
.title {
    font-size: 36px;
    font-weight: 800;
    padding: 8px 0;
}
.sub {
    color: #888;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🛠️ Code Review Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Analyze Java code using text input or file uploads. Backend: Spring Boot API.</div>', unsafe_allow_html=True)

# Hide Streamlit footer + menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# =========================================================
# CUSTOM VALIDATION RULES (MATCHED WITH BACKEND)
# =========================================================
VALIDATION_RULES = [
    "Avoid System.out.println — use a proper logger.",
    "Avoid empty catch blocks — always handle exceptions.",
    "Avoid hardcoded passwords, tokens, or URLs.",
    "Methods should not exceed 50 lines.",
    "Classes should follow single responsibility principle.",
    "Use constructor injection instead of field injection.",
    "Do not call the database directly from controllers.",
    "Avoid using raw types — always specify generics.",
    "Prefer Optional over returning null.",
    "Avoid deeply nested if/else blocks — refactor logic."
]


# =========================================================
# SIDEBAR — Show Validation Rules
# =========================================================
st.sidebar.header("📘 Validation Rules")
for rule in VALIDATION_RULES:
    st.sidebar.markdown(f"✔ **{rule}**")

st.sidebar.markdown("---")
st.sidebar.header("💡 Tips")
st.sidebar.info("""
- Upload multiple Java files for batch review.
- Paste mode works best for small snippets.
- Backend uses OpenAI if OPENAI_API_KEY is set.
- You can upload XML/JSON/properties files to analyze configs too.
""")


# =========================================================
# MODE SELECTION
# =========================================================
mode = st.radio(
    "Choose Mode:",
    ["💬 Paste Code", "📁 Upload Files"],
    horizontal=True
)

backend_url = "http://localhost:8080/api/review"


# =========================================================
# HELPER — Render GitHub-Style Diff
# =========================================================
def render_diff(original_text, improved_text, left_name="Original", right_name="Improved"):
    original = original_text.splitlines()
    improved = improved_text.splitlines()

    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_table(
        original, improved,
        fromdesc=left_name,
        todesc=right_name,
        context=True,
        numlines=3
    )

    styled_html = f"""
    <style>
    table.diff {{width: 100%; font-family: Consolas, monospace; font-size: 13px; border-collapse: collapse;}}
    .diff_header {{background: #f7f7f7; font-weight: bold; padding: 4px;}}
    .diff_next {{background: #f0f0f0; padding: 4px;}}
    .diff_add {{background: #e6ffed !important;}}
    .diff_sub {{background: #ffeef0 !important;}}
    .diff_chg {{background: #fff5b1 !important;}}
    td {{padding: 2px 6px;}}
    </style>
    {html_diff}
    """

    components.html(styled_html, height=500, scrolling=True)


# =========================================================
# MODE 1 — PASTE CODE
# =========================================================
if mode == "💬 Paste Code":
    st.markdown("### ✏️ Input Java Code")
    code = st.text_area("", height=300, placeholder="public class Hello { ... }")

    if st.button("🚀 Analyze Code", use_container_width=True):
        if not code.strip():
            st.warning("⚠ Please paste some Java code first.")
        else:
            with st.spinner("Analyzing code..."):
                try:
                    response = requests.post(backend_url, json={"code": code}, timeout=120)

                    if response.status_code == 200:
                        data = response.json()

                        tabs = st.tabs([
                            "🐞 Bugs",
                            "🔐 Security Issues",
                            "💨 Code Smells",
                            "💡 Suggestions",
                            "🛑 Custom Validations",
                            "🧾 Improved Code + Diff",
                            "📘 Rules Applied"
                        ])

                        # ========== BUGS ==========
                        with tabs[0]:
                            st.markdown("### 🐞 Bugs Found")
                            bugs = data.get("bugs", [])
                            if bugs:
                                for b in bugs:
                                    st.error(f"• {b}")
                            else:
                                st.success("No bugs found 🎉")

                        # ========== SECURITY ==========
                        with tabs[1]:
                            st.markdown("### 🔐 Security Issues")
                            sec = data.get("security_issues", [])
                            if sec:
                                for s in sec:
                                    st.warning(f"• {s}")
                            else:
                                st.success("No security issues ✔")

                        # ========== CODE SMELLS ==========
                        with tabs[2]:
                            st.markdown("### 💨 Code Smells")
                            smells = data.get("code_smells", [])
                            if smells:
                                for sm in smells:
                                    st.info(f"• {sm}")
                            else:
                                st.success("No code smells 👍")

                        # ========== SUGGESTIONS ==========
                        with tabs[3]:
                            st.markdown("### 💡 Suggestions")
                            sugg = data.get("suggestions", [])
                            if sugg:
                                for sg in sugg:
                                    st.write(f"🔸 {sg}")
                            else:
                                st.success("No suggestions.")

                        # ========== CUSTOM VALIDATIONS ==========
                        with tabs[4]:
                            st.markdown("### 🛑 Custom Validation Rules (Strict Rules Applied)")
                            custom = data.get("custom_validations", [])
                            if custom:
                                for rule in custom:
                                    st.error("• " + rule)
                            else:
                                st.success("No custom validation issues ✔")

                        # ========== IMPROVED CODE + DIFF ==========
                        with tabs[5]:
                            improved = data.get("improved_code", "")

                            if not improved or improved.strip() == "":
                                st.info("⚠ The model did not generate improved code. Showing original.")
                                improved = code

                            st.markdown("### 🔍 Differences (Original → Improved)")
                            render_diff(code, improved, "Your Code", "Improved Code")

                            st.markdown("### ✔ Final Improved Code (Full)")
                            st.code(improved, language="java")

                        # ========== RULES APPLIED ==========
                        with tabs[6]:
                            st.markdown("### 📘 Validation Rules Applied")

                            all_issues = (
                                    data.get("bugs", []) +
                                    data.get("security_issues", []) +
                                    data.get("code_smells", []) +
                                    data.get("suggestions", []) +
                                    data.get("custom_validations", [])
                            )

                            applied = []
                            for rule in VALIDATION_RULES:
                                keyword = rule.split(" — ")[0].lower()
                                if any(keyword in issue.lower() for issue in all_issues):
                                    applied.append(rule)

                            if applied:
                                for r in applied:
                                    st.markdown(f"✔ **{r}**")
                            else:
                                st.success("No validation rules triggered.")

                    else:
                        st.error(f"❌ Backend Error: {response.status_code}\n{response.text}")

                except Exception as e:
                    st.error(f"🔥 Failed to connect to backend: {e}")


# =========================================================
# MODE 2 — UPLOAD FILES
# =========================================================
elif mode == "📁 Upload Files":

    st.markdown("### 📂 Upload Java or text files")
    uploaded_files = st.file_uploader(
        "Choose one or more files",
        type=["java", "txt", "xml", "json", "properties"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("🚀 Analyze Uploaded Files", use_container_width=True):

        for file in uploaded_files:
            st.markdown(f"## 📄 File: **{file.name}**")
            file_content = file.read().decode("utf-8", errors="ignore")

            with st.spinner(f"Analyzing {file.name}..."):
                try:
                    response = requests.post(backend_url, json={"code": file_content}, timeout=120)

                    if response.status_code == 200:
                        data = response.json()

                        with st.expander(f"📌 Analysis for {file.name}", expanded=True):

                            st.subheader("🐞 Bugs")
                            for b in data.get("bugs", []):
                                st.error(f"• {b}")

                            st.subheader("🔐 Security Issues")
                            for s in data.get("security_issues", []):
                                st.warning(f"• {s}")

                            st.subheader("💨 Code Smells")
                            for sm in data.get("code_smells", []):
                                st.info(f"• {sm}")

                            st.subheader("💡 Suggestions")
                            for sg in data.get("suggestions", []):
                                st.write(f"🔸 {sg}")

                            # ===== CUSTOM VALIDATIONS =====
                            st.subheader("🛑 Custom Validations")
                            custom = data.get("custom_validations", [])
                            if custom:
                                for cv in custom:
                                    st.error("• " + cv)
                            else:
                                st.success("No custom validation issues ✔")

                            # ===== DIFF VIEW =====
                            st.markdown("### 🔍 Differences (Original → Improved)")
                            improved = data.get("improved_code", "")
                            if not improved.strip():
                                improved = file_content

                            render_diff(file_content, improved, file.name + " (Original)", file.name + " (Improved)")

                            # ===== FINAL IMPROVED CODE =====
                            st.markdown("### ✔ Final Improved Code (Full)")
                            st.code(improved, language="java")

                            # ===== RULES APPLIED =====
                            st.subheader("📘 Rules Applied")

                            all_issues = (
                                    data.get("bugs", []) +
                                    data.get("security_issues", []) +
                                    data.get("code_smells", []) +
                                    data.get("suggestions", []) +
                                    data.get("custom_validations", [])
                            )

                            applied_rules = []
                            for rule in VALIDATION_RULES:
                                keyword = rule.split(" — ")[0].lower()
                                if any(keyword in issue.lower() for issue in all_issues):
                                    applied_rules.append(rule)

                            if applied_rules:
                                for r in applied_rules:
                                    st.markdown(f"✔ **{r}**")
                            else:
                                st.success("No validation rules triggered.")

                    else:
                        st.error(f"❌ Backend error for {file.name}: {response.status_code}")

                except Exception as e:
                    st.error(f"🔥 Failed processing file {file.name}: {str(e)}")
