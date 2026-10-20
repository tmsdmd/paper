import os
import tempfile

import pandas as pd
import streamlit as st

from database import (
    add_note,
    add_paper,
    add_task,
    create_project,
    delete_paper,
    get_all_langs,
    get_all_source_types,
    get_default_project_id,
    get_paper,
    get_stats,
    init_db,
    list_papers,
    list_projects,
    list_tasks,
)
from pdf_export import export_papers_pdf
from research_api import fetch_research

TRANSLATIONS = {
    "Arabic": {
        "title": "Paper Research Hub",
        "subtitle": "نظام بحث علمي شخصي لإدارة البحوث والرسائل والمراجع",
        "dashboard": "لوحة التحكم",
        "search": "البحث في الإنترنت",
        "library": "المكتبة",
        "compare": "المقارنة",
        "export": "تصدير PDF",
        "new_project": "مشروع جديد",
        "project_name": "اسم المشروع",
        "project_topic": "موضوع المشروع",
        "project_description": "وصف المشروع",
        "project_language": "لغة المشروع",
        "create": "إنشاء",
        "search_topic": "موضوع البحث",
        "search_btn": "بحث في arXiv و Crossref",
        "manual_add": "إضافة يدويّة",
        "title_field": "العنوان",
        "authors": "المؤلفون",
        "year": "السنة",
        "source_name": "اسم المصدر",
        "source_url": "رابط المصدر",
        "source_type": "نوع المصدر",
        "abstract": "الملخص",
        "keywords": "الكلمات المفتاحية",
        "summary": "التلخيص",
        "notes": "ملاحظات",
        "language": "اللغة",
        "save": "حفظ السجل",
        "total_records": "إجمالي السجلات",
        "latest": "آخر سجل",
        "filter_language": "تصفية حسب اللغة",
        "filter_type": "تصفية حسب النوع",
        "search_library": "بحث في المكتبة",
        "select_record": "اختر سجلًا لعرض تفاصيله",
        "add_note": "إضافة ملاحظة",
        "delete": "حذف",
        "records": "السجلات",
        "download_arabic": "تحميل PDF عربي",
        "download_english": "تحميل PDF إنجليزي",
        "export_title": "تصدير تقرير",
        "tasks": "المهام",
        "task_title": "عنوان المهمة",
        "task_status": "الحالة",
        "task_detail": "التفاصيل",
        "task_add": "إضافة مهمة",
        "empty": "لا توجد سجلات بعد",
    },
    "English": {
        "title": "Paper Research Hub",
        "subtitle": "Personal research system for papers, theses, and academic references",
        "dashboard": "Dashboard",
        "search": "Web Search",
        "library": "Library",
        "compare": "Comparison",
        "export": "PDF Export",
        "new_project": "New Project",
        "project_name": "Project Name",
        "project_topic": "Project Topic",
        "project_description": "Project Description",
        "project_language": "Project Language",
        "create": "Create",
        "search_topic": "Research Topic",
        "search_btn": "Search arXiv and Crossref",
        "manual_add": "Manual Entry",
        "title_field": "Title",
        "authors": "Authors",
        "year": "Year",
        "source_name": "Source Name",
        "source_url": "Source URL",
        "source_type": "Source Type",
        "abstract": "Abstract",
        "keywords": "Keywords",
        "summary": "Summary",
        "notes": "Notes",
        "language": "Language",
        "save": "Save record",
        "total_records": "Total Records",
        "latest": "Latest Entry",
        "filter_language": "Filter by language",
        "filter_type": "Filter by type",
        "search_library": "Search library",
        "select_record": "Select a record to inspect",
        "add_note": "Add note",
        "delete": "Delete",
        "records": "Records",
        "download_arabic": "Download Arabic PDF",
        "download_english": "Download English PDF",
        "export_title": "Export report",
        "tasks": "Tasks",
        "task_title": "Task title",
        "task_status": "Status",
        "task_detail": "Details",
        "task_add": "Add task",
        "empty": "No records yet",
    },
}


def current_language():
    return st.session_state.get("app_language", "Arabic")


def t(key):
    return TRANSLATIONS.get(current_language(), TRANSLATIONS["Arabic"]).get(key, key)


st.set_page_config(page_title="Paper Research Hub", page_icon="📚", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #070b11 0%, #0e1622 55%, #101a29 100%);
        color: #edf3ff;
    }
    [data-testid="stSidebar"] {
        background: rgba(12,15,22,0.95);
        border-right: 1px solid #2b3447;
    }
    .stApp {
        background: transparent;
    }
    div[data-testid="stVerticalBlock"] > div {
        border: 1px solid #2b3447;
        border-radius: 14px;
        background: rgba(20,25,36,0.78);
        padding: 10px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3366ff, #66d9ff);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stNumberInput input {
        background: #121a28;
        color: white;
        border: 1px solid #2d3b52;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #f7fbff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

if "app_language" not in st.session_state:
    st.session_state.app_language = "Arabic"

if "project_id" not in st.session_state:
    st.session_state.project_id = get_default_project_id()

with st.sidebar:
    st.title("📚")
    st.subheader(t("title"))
    st.caption(t("subtitle"))

    lang_options = ["Arabic", "English"]
    current_index = 0 if st.session_state.app_language == "Arabic" else 1
    st.session_state.app_language = st.selectbox("Language / اللغة", lang_options, index=current_index)

    st.markdown("---")
    st.subheader(t("new_project"))
    project_name = st.text_input(t("project_name"), placeholder="My thesis project")
    project_topic = st.text_input(t("project_topic"), placeholder="AI in education")
    project_desc = st.text_area(t("project_description"), height=80)
    if st.button(t("create")):
        if project_name.strip():
            new_id = create_project(project_name.strip(), project_topic.strip(), project_desc.strip(), st.session_state.app_language)
            st.session_state.project_id = new_id
            st.success("Project created")
            st.rerun()

    st.markdown("---")
    projects = list_projects()
    if projects:
        options = {p["name"]: p["id"] for p in projects}
        selected_project_name = st.selectbox("Project / المشروع", list(options.keys()))
        st.session_state.project_id = options[selected_project_name]

project_id = st.session_state.project_id

if project_id is None:
    project_id = get_default_project_id()
    st.session_state.project_id = project_id


tab_dashboard, tab_search, tab_library, tab_compare, tab_export = st.tabs([
    t("dashboard"),
    t("search"),
    t("library"),
    t("compare"),
    t("export"),
])

with tab_dashboard:
    st.title(t("title"))
    st.caption(t("subtitle"))
    stats = get_stats(project_id)
    c1, c2, c3 = st.columns(3)
    c1.metric(t("total_records"), stats["total"])
    c2.metric("Project", list_projects()[0]["name"] if list_projects() else "No project")
    c3.metric(t("latest"), stats["latest"][:35])

    st.markdown("### Tasks")
    task_title = st.text_input(t("task_title"), key="task_title_input")
    task_status = st.selectbox(t("task_status"), ["Open", "In Progress", "Done"], key="task_status_input")
    task_detail = st.text_area(t("task_detail"), height=80, key="task_detail_input")
    if st.button(t("task_add")):
        if task_title.strip():
            add_task(project_id, task_title.strip(), task_status, task_detail.strip())
            st.success("Task added")
            st.rerun()
    tasks = list_tasks(project_id)
    if tasks:
        task_df = pd.DataFrame(tasks)
        st.dataframe(task_df[["title", "status", "detail", "created_at"]], use_container_width=True)
    else:
        st.info(t("empty"))

with tab_search:
    st.title(t("search"))
    topic = st.text_input(t("search_topic"), placeholder="AI for healthcare decision support")
    max_results = st.slider("Max results / عدد النتائج", 3, 20, 5)
    if st.button(t("search_btn")):
        if topic.strip():
            results = fetch_research(topic.strip(), max_results=max_results)
            st.session_state.search_results = results
            st.success(f"Found {len(results)} results")

    if "search_results" in st.session_state:
        for idx, item in enumerate(st.session_state.search_results):
            with st.container():
                st.markdown(f"### {item.get('title', '')}")
                st.write(f"Authors: {item.get('authors', '')}")
                st.write(f"Source: {item.get('source_name', '')} | Year: {item.get('year', '')}")
                st.write(item.get('summary', ''))
                if st.button("Save to library / حفظ في المكتبة", key=f"save_result_{idx}"):
                    add_paper(
                        project_id=project_id,
                        title=item.get('title', ''),
                        authors=item.get('authors', ''),
                        year=int(item.get('year', 0)) if str(item.get('year', '')).isdigit() else None,
                        source_name=item.get('source_name', ''),
                        source_url=item.get('source_url', ''),
                        source_type=item.get('source_type', 'arXiv'),
                        abstract=item.get('abstract', ''),
                        summary=item.get('summary', ''),
                        keywords=item.get('keywords', ''),
                        notes="Imported from web search",
                        language=item.get('language', 'English'),
                    )
                    st.success("Saved")
                    st.rerun()
                st.markdown("---")

with tab_library:
    st.title(t("library"))
    search_query = st.text_input(t("search_library"), placeholder="Search title, author, or keyword")
    filter_lang = st.selectbox(t("filter_language"), get_all_langs(), index=0)
    filter_type = st.selectbox(t("filter_type"), get_all_source_types(), index=0)
    records = list_papers(project_id=project_id, query=search_query, language=filter_lang, source_type=filter_type)

    if records:
        df = pd.DataFrame(records)
        display_cols = ["title", "authors", "source_name", "source_type", "year", "language"]
        st.dataframe(df[display_cols], use_container_width=True)

        rec_list = ["--"] + [r["title"] for r in records]
        selected_title = st.selectbox(t("select_record"), rec_list)
        if selected_title != "--":
            selected = next(r for r in records if r["title"] == selected_title)
            record_id = selected["id"]
            st.markdown(f"### {selected['title']}")
            st.write(f"Authors: {selected.get('authors', '')}")
            st.write(f"Source: {selected.get('source_name', '')} | Type: {selected.get('source_type', '')} | Year: {selected.get('year', '')}")
            st.write(f"Summary: {selected.get('summary', '')}")
            st.write(f"Abstract: {selected.get('abstract', '')}")
            st.write(f"Keywords: {selected.get('keywords', '')}")
            st.write(f"Notes: {selected.get('notes', '')}")

            if st.button(f"{t('delete')} - {selected['title']}"):
                delete_paper(record_id)
                st.success("Record deleted")
                st.rerun()

            note_text = st.text_area("Add note / إضافة ملاحظة", height=100)
            if st.button(t("add_note")):
                if note_text.strip():
                    add_note(record_id, note_text)
                    st.success("Note saved")
                    st.rerun()
    else:
        st.info(t("empty"))

with tab_compare:
    st.title(t("compare"))
    records = list_papers(project_id=project_id)
    if records:
        choices = [f"{r['id']} - {r['title']}" for r in records]
        selected_ids = st.multiselect("Select records", choices)
        if selected_ids:
            selected_records = []
            for choice in selected_ids:
                rec_id = int(choice.split(" - ", 1)[0])
                selected_records.append(get_paper(rec_id))
            compare_df = pd.DataFrame(
                [
                    {
                        "Title": r["title"],
                        "Authors": r["authors"],
                        "Year": r["year"],
                        "Source": r["source_name"],
                        "Type": r["source_type"],
                        "Language": r["language"],
                        "Summary": r["summary"],
                    }
                    for r in selected_records if r is not None
                ]
            )
            st.dataframe(compare_df, use_container_width=True)
    else:
        st.info(t("empty"))

with tab_export:
    st.title(t("export_title"))
    records = list_papers(project_id=project_id)
    if records:
        selected_titles = st.multiselect("Select papers for export / اختر الأوراق للتصدير", [r["title"] for r in records])
        if selected_titles:
            filtered = [r for r in records if r["title"] in selected_titles]
            export_dir = os.path.join(tempfile.gettempdir(), "paper_exports")
            os.makedirs(export_dir, exist_ok=True)

            arabic_path = os.path.join(export_dir, "research_report_arabic.pdf")
            english_path = os.path.join(export_dir, "research_report_english.pdf")

            export_papers_pdf(filtered, arabic_path, language="Arabic")
            export_papers_pdf(filtered, english_path, language="English")

            with open(arabic_path, "rb") as f:
                arabic_data = f.read()
            with open(english_path, "rb") as f:
                english_data = f.read()

            st.download_button(t("download_arabic"), data=arabic_data, file_name="research_report_arabic.pdf", mime="application/pdf")
            st.download_button(t("download_english"), data=english_data, file_name="research_report_english.pdf", mime="application/pdf")
    else:
        st.info(t("empty"))

st.markdown("---")
st.caption("Paper Research Hub — Academic Research Management Platform")
