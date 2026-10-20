import os
import tempfile

import pandas as pd
import streamlit as st

from database import (
    add_note,
    add_paper,
    add_research_gap,
    add_review,
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
    list_research_gaps,
    list_reviews,
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
        "gap": "فجوة بحثية",
        "review": "مراجعة أدبية",
        "roadmap": "خطة الأطروحة",
        "writer": "توليد النصوص",
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
        "gap_topic": "موضوع فجوة البحث",
        "gap_summary": "ملخص الفجوة",
        "gap_analysis": "تحليل الفجوة",
        "gap_recommendations": "التوصيات",
        "save_gap": "حفظ الفجوة",
        "review_title": "عنوان المراجعة الأدبية",
        "review_content": "محتوى المراجعة الأدبية",
        "save_review": "حفظ المراجعة",
        "roadmap_title": "عنوان الخطة",
        "roadmap_content": "محتوى خطة الأطروحة",
        "save_roadmap": "حفظ الخطة",
        "generate_text": "توليد نص عربي/إنجليزي",
        "generated_text": "النص المولّد",
        "empty": "لا توجد سجلات بعد",
        "text_template": "القالب النصي",
        "intro": "مقدمة الأطروحة",
        "objectives": "أهداف البحث",
        "questions": "أسئلة البحث",
        "chapter1": "خطة الفصل الأول",
        "select_papers": "اختر الأوراق",
        "generate": "توليد",
        "comparison_summary": "ملخص المقارنة",
        "analysis_result": "نتيجة التحليل",
        "research_gap_note": "تم بناء الفجوة البحثية من خلال مقارنة الأوراق المختارة",
    },
    "English": {
        "title": "Paper Research Hub",
        "subtitle": "Personal research system for papers, theses, and academic references",
        "dashboard": "Dashboard",
        "search": "Web Search",
        "library": "Library",
        "compare": "Comparison",
        "gap": "Research Gap",
        "review": "Literature Review",
        "roadmap": "Thesis Roadmap",
        "writer": "Text Generator",
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
        "gap_topic": "Research gap topic",
        "gap_summary": "Gap summary",
        "gap_analysis": "Gap analysis",
        "gap_recommendations": "Recommendations",
        "save_gap": "Save gap",
        "review_title": "Literature review title",
        "review_content": "Literature review content",
        "save_review": "Save review",
        "roadmap_title": "Roadmap title",
        "roadmap_content": "Thesis roadmap content",
        "save_roadmap": "Save roadmap",
        "generate_text": "Generate Arabic/English text",
        "generated_text": "Generated text",
        "empty": "No records yet",
        "text_template": "Text template",
        "intro": "Thesis introduction",
        "objectives": "Research objectives",
        "questions": "Research questions",
        "chapter1": "Chapter 1 plan",
        "select_papers": "Select papers",
        "generate": "Generate",
        "comparison_summary": "Comparison summary",
        "analysis_result": "Analysis result",
        "research_gap_note": "The research gap was derived by comparing the selected papers.",
    },
}


def current_language():
    return st.session_state.get("app_language", "Arabic")


def t(key):
    return TRANSLATIONS.get(current_language(), TRANSLATIONS["Arabic"]).get(key, key)


def text_or_empty(value):
    return str(value or "").strip()


def safe_list(records):
    return records if records else []


def build_compare_summary(records, language="Arabic"):
    if not records:
        return "" if language == "Arabic" else ""

    items = []
    for item in records:
        title = text_or_empty(item.get("title"))
        summary = text_or_empty(item.get("summary")) or text_or_empty(item.get("abstract"))
        authors = text_or_empty(item.get("authors"))
        year = text_or_empty(item.get("year"))
        items.append(f"- {title} ({authors}, {year}): {summary[:220]}")

    if language == "Arabic":
        return (
            "تمت مقارنة الأوراق المختارة على أساس الموضوع، المنهجية، النتائج، والفجوة البحثية. "
            "الملاحظات الأساسية هي:\n" + "\n".join(items[:8])
        )
    return "The selected papers were compared on theme, methodology, results, and research gaps. Key observations:\n" + "\n".join(items[:8])


def build_research_gap_text(records, language="Arabic"):
    if not records:
        return (
            "لا توجد بيانات كافية لتحديد فجوة بحثية."
            if language == "Arabic"
            else "There is insufficient evidence to identify a research gap."
        )

    highlights = []
    for item in records:
        title = text_or_empty(item.get("title"))
        summary = text_or_empty(item.get("summary")) or text_or_empty(item.get("abstract"))
        if summary:
            highlights.append(f"- {title}: {summary[:180]}")

    if language == "Arabic":
        return (
            "بناءً على مقارنة الأوراق المختارة، تظهر الفجوة البحثية في أن أغلب الدراسات تركز على ... بينما لا توجد دراسات كافية تتناول ... "
            "وبالتالي، يبرز احتياج إلى دراسة تركز على تقييم الواقع العملي، قياس الأداء في بيئة حقيقية، وتطوير حلول قابلة للتنفيذ. "
            "ملاحظات المقارنة:\n" + "\n".join(highlights[:6])
        )
    return (
        "Based on the selected studies, the research gap is that most prior work focuses on ... while limited evidence exists on ... "
        "This suggests a need for a practical, real-world evaluation approach that measures performance in natural settings and connects the solution to actionable outcomes. "
        "Comparison notes:\n" + "\n".join(highlights[:6])
    )


def build_literature_review(records, language="Arabic"):
    if not records:
        return "" if language == "Arabic" else ""

    intro = (
        "تسعى هذه المراجعة الأدبية إلى تحليل الدراسات السابقة ذات الصلة بموضوع البحث، ومقارنة أساليبها، والنتائج الأساسية، والفجوات التي لا تزال قائمة."
        if language == "Arabic"
        else "This literature review examines prior studies related to the research topic, compares their methods and outcomes, and identifies the remaining gaps."
    )

    sections = [intro]
    for i, paper in enumerate(records[:8], start=1):
        title = text_or_empty(paper.get("title"))
        summary = text_or_empty(paper.get("summary")) or text_or_empty(paper.get("abstract"))
        authors = text_or_empty(paper.get("authors"))
        year = text_or_empty(paper.get("year"))
        if language == "Arabic":
            sections.append(
                f"{i}. {title} ({authors}, {year}). ركزت هذه الدراسة على {summary[:200]} ... "
                "وهي تمثل نقطة مهمة في مسار البحث، لكنها لا تزال تفتقد إلى ..."
            )
        else:
            sections.append(
                f"{i}. {title} ({authors}, {year}). This study focused on {summary[:200]} ... "
                "It contributes important evidence, but it still leaves a gap concerning ..."
            )

    closing = (
        "وبناءً على هذه المراجعة، يمكن استخلاص أن التقدم العلمي في هذا المجال يركز على ... مع وجود حاجة واضحة إلى ... لتطوير حلول أكثر عمقًا وتطبيقًا."
        if language == "Arabic"
        else "Based on this review, the field has advanced in ... while there remains a need for ... to support more complete and practical solutions."
    )
    sections.append(closing)
    return "\n\n".join(sections)


def build_thesis_roadmap(records, language="Arabic"):
    if not records:
        return "" if language == "Arabic" else ""

    if language == "Arabic":
        return (
            "خطة الأطروحة:\n\n"
            "الفصل الأول: مقدمة البحث\n"
            "- تقديم المشكلة\n"
            "- أهمية الدراسة\n"
            "- أهداف البحث\n"
            "- أسئلة البحث\n"
            "- حدود الدراسة\n\n"
            "الفصل الثاني: مراجعة الأدبيات\n"
            "- مراجعة البحوث المرتبطة\n"
            "- تحليل المقارنات\n"
            "- تحديد الفجوة البحثية\n\n"
            "الفصل الثالث: المنهجية\n"
            "- تصميم الدراسة\n"
            "- مجتمع وعينة البحث\n"
            "- أدوات جمع البيانات\n"
            "- أساليب التحليل\n\n"
            "الفصل الرابع: التنفيذ والتحليل\n"
            "- تطبيق الحل أو النموذج\n"
            "- تحليل النتائج\n"
            "- مناقشة النتائج\n\n"
            "الفصل الخامس: الخاتمة والتوصيات\n"
            "- ملخص النتائج\n"
            "- التوصيات\n"
            "- المقترحات المستقبلية\n\n"
            "ملاحظات استنادًا إلى الأوراق المختارة: " + ", ".join(text_or_empty(p.get("title")) for p in records[:5])
        )
    return (
        "Thesis roadmap:\n\n"
        "Chapter 1: Introduction\n"
        "- Problem statement\n"
        "- Significance of the study\n"
        "- Research objectives\n"
        "- Research questions\n"
        "- Scope and delimitations\n\n"
        "Chapter 2: Literature Review\n"
        "- Review of related studies\n"
        "- Comparative analysis\n"
        "- Gap identification\n\n"
        "Chapter 3: Methodology\n"
        "- Study design\n"
        "- Population and sampling\n"
        "- Data collection tools\n"
        "- Data analysis methods\n\n"
        "Chapter 4: Implementation and Analysis\n"
        "- System or model implementation\n"
        "- Results analysis\n"
        "- Discussion of findings\n\n"
        "Chapter 5: Conclusion and Recommendations\n"
        "- Summary of findings\n"
        "- Recommendations\n"
        "- Future research directions\n\n"
        "Notes from selected papers: " + ", ".join(text_or_empty(p.get("title")) for p in records[:5])
    )


def build_introduction_text(records, language="Arabic"):
    topic_name = "موضوع البحث" if language == "Arabic" else "research topic"
    paper_names = ", ".join(text_or_empty(p.get("title")) for p in records[:3])
    if language == "Arabic":
        return (
            f"تتعلق هذه الدراسة بـ {topic_name}، ويرتكزها على مراجعة الدراسات السابقة ذات الصلة، بما في ذلك {paper_names}. "
            "تسعى الدراسة إلى فهم المشكلات الحالية، وتحليلها، وتحديد الفجوة البحثية، ثم تقديم إطار عملي أو نظري يساهم في تطوير الحل المقترح."
        )
    return (
        f"This study is concerned with the {topic_name}, and is grounded in a review of related prior work including {paper_names}. "
        "The study seeks to understand the current problems, analyze them, identify the research gap, and then propose a practical or theoretical framework that advances the suitable solution."
    )


def build_objectives_text(records, language="Arabic"):
    if language == "Arabic":
        return (
            "1. تحليل الدراسات السابقة ذات الصلة بموضوع البحث.\n"
            "2. تحديد الفجوة البحثية الحالية ومجالات الحاجة إلى تطوير إضافي.\n"
            "3. تقييم المزايا والقيود في الحلول الحالية.\n"
            "4. اقتراح حل أو إطار عملي يراعي الواقع البحثي والتطبيقي.\n"
            "5. تقديم خطة مناسبة لتطبيق الدراسة ومناقشة النتائج."
        )
    return (
        "1. Review related studies in the relevant field.\n"
        "2. Identify the current research gap and the need for further development.\n"
        "3. Evaluate strengths and limitations in existing solutions.\n"
        "4. Propose a practical framework or solution informed by the evidence.\n"
        "5. Present a clear plan for implementation and results discussion."
    )


def build_research_questions_text(records, language="Arabic"):
    if language == "Arabic":
        return (
            "1. ما هي التحديات الرئيسية المرتبطة بموضوع البحث؟\n"
            "2. ما هي الفجوة البحثية الحالية بين الدراسات السابقة والحاجة العملية؟\n"
            "3. ما هي الحلول أو الأطر المقترحة في الأدبيات؟\n"
            "4. كيف يمكن تصميم حل عملي أو نموذجي يراعي الواقع؟\n"
            "5. ما هي مؤشرات النجاح أو المقاييس المناسبة لتقييم الحل؟"
        )
    return (
        "1. What are the main challenges related to the research topic?\n"
        "2. What is the current research gap between existing studies and real-world needs?\n"
        "3. What solutions or frameworks are commonly proposed in the literature?\n"
        "4. How can a practical or model-based solution be designed to fit the real context?\n"
        "5. What success indicators or evaluation metrics are appropriate for the solution?"
    )


def build_chapter1_plan(records, language="Arabic"):
    if language == "Arabic":
        return (
            "الفصل الأول: مقدمة البحث\n\n"
            "1. خلفية المشكلة\n"
            "2. بيان المشكلة\n"
            "3. أهمية البحث\n"
            "4. أسئلة البحث\n"
            "5. أهداف البحث\n"
            "6. حدود البحث\n"
            "7. منهجية الدراسة\n"
            "8. هيكل الأطروحة\n"
            "9. ملخص السياسة أو الهدف البحثي"
        )
    return (
        "Chapter 1: Introduction\n\n"
        "1. Background of the problem\n"
        "2. Statement of the problem\n"
        "3. Significance of the study\n"
        "4. Research questions\n"
        "5. Objectives of the study\n"
        "6. Scope and limitations\n"
        "7. Research methodology\n"
        "8. Structure of the thesis\n"
        "9. Summary of the research objective"
    )


def generate_text_for_selection(selected_titles, records, template, language="Arabic"):
    filtered = [r for r in records if r["title"] in selected_titles]
    if not filtered:
        return "" if language == "Arabic" else ""

    if template == "intro":
        return build_introduction_text(filtered, language)
    if template == "objectives":
        return build_objectives_text(filtered, language)
    if template == "questions":
        return build_research_questions_text(filtered, language)
    if template == "chapter1":
        return build_chapter1_plan(filtered, language)
    if template == "compare":
        return build_compare_summary(filtered, language)
    if template == "gap":
        return build_research_gap_text(filtered, language)
    if template == "review":
        return build_literature_review(filtered, language)
    if template == "roadmap":
        return build_thesis_roadmap(filtered, language)
    return ""


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


tab_dashboard, tab_search, tab_library, tab_compare, tab_gap, tab_review, tab_roadmap, tab_writer, tab_export = st.tabs([
    t("dashboard"),
    t("search"),
    t("library"),
    t("compare"),
    t("gap"),
    t("review"),
    t("roadmap"),
    t("writer"),
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
            st.markdown("### " + t("comparison_summary"))
            st.write(build_compare_summary(selected_records, current_language()))
    else:
        st.info(t("empty"))

with tab_gap:
    st.title(t("gap"))
    records = list_papers(project_id=project_id)
    if records:
        choices = [r["title"] for r in records]
        selected_titles = st.multiselect(t("select_papers"), choices)
        if selected_titles:
            selected_records = [r for r in records if r["title"] in selected_titles]
            gap_text = build_research_gap_text(selected_records, current_language())
            st.markdown("### " + t("analysis_result"))
            st.write(gap_text)

            gap_topic = st.text_input(t("gap_topic"), value=selected_titles[0] if selected_titles else "")
            gap_summary = st.text_area(t("gap_summary"), value=gap_text[:500], height=120)
            gap_analysis = st.text_area(t("gap_analysis"), value=gap_text, height=150)
            gap_recommendations = st.text_area(t("gap_recommendations"), value="- توصي الدراسة بزيادة التقييم العملي\n- توصي بشرح الأساليب بشكل أعمق\n- توصي ببناء حل قابل للتطبيق في بيئة حقيقية", height=120)
            if st.button(t("save_gap")):
                if gap_topic.strip():
                    add_research_gap(project_id, gap_topic.strip(), gap_summary.strip(), gap_analysis.strip(), gap_recommendations.strip())
                    st.success("Research gap saved")
                    st.rerun()

        stored_gaps = list_research_gaps(project_id)
        if stored_gaps:
            st.markdown("### Saved research gaps")
            for g in stored_gaps:
                st.markdown("---")
                st.markdown(f"### {g['topic']}")
                st.write(f"Summary: {g['summary']}")
                st.write(f"Gap: {g['research_gap']}")
                st.write(f"Recommendations: {g['recommendations']}")
    else:
        st.info(t("empty"))

with tab_review:
    st.title(t("review"))
    records = list_papers(project_id=project_id)
    if records:
        choices = [r["title"] for r in records]
        selected_titles = st.multiselect(t("select_papers"), choices)
        if selected_titles:
            selected_records = [r for r in records if r["title"] in selected_titles]
            if st.button("Generate review / توليد مراجعة"):
                generated = build_literature_review(selected_records, current_language())
                st.session_state.generated_review = generated
            if "generated_review" in st.session_state:
                st.markdown("### Generated Review")
                st.write(st.session_state.generated_review)
                review_title = st.text_input(t("review_title"), value="Literature Review")
                review_content = st.text_area(t("review_content"), value=st.session_state.generated_review, height=260)
                if st.button(t("save_review")):
                    add_review(project_id, review_title.strip() or "Literature Review", review_content.strip())
                    st.success("Literature review saved")
                    st.rerun()

        reviews = list_reviews(project_id)
        if reviews:
            for item in reviews:
                st.markdown("---")
                st.markdown(f"### {item['title']}")
                st.write(item['content'])
    else:
        st.info(t("empty"))

with tab_roadmap:
    st.title(t("roadmap"))
    records = list_papers(project_id=project_id)
    if records:
        choices = [r["title"] for r in records]
        selected_titles = st.multiselect(t("select_papers"), choices)
        if selected_titles:
            selected_records = [r for r in records if r["title"] in selected_titles]
            if st.button("Generate roadmap / توليد خطة"):
                roadmap_text = build_thesis_roadmap(selected_records, current_language())
                st.session_state.generated_roadmap = roadmap_text
            if "generated_roadmap" in st.session_state:
                st.markdown("### Generated roadmap")
                st.write(st.session_state.generated_roadmap)
                roadmap_title = st.text_input(t("roadmap_title"), value="Thesis Roadmap")
                roadmap_content = st.text_area(t("roadmap_content"), value=st.session_state.generated_roadmap, height=260)
                if st.button(t("save_roadmap")):
                    add_review(project_id, roadmap_title.strip() or "Thesis Roadmap", roadmap_content.strip())
                    st.success("Roadmap saved")
                    st.rerun()
    else:
        st.info(t("empty"))

with tab_writer:
    st.title(t("writer"))
    records = list_papers(project_id=project_id)
    if records:
        choices = [r["title"] for r in records]
        selected_titles = st.multiselect(t("select_papers"), choices)
        language_choice = st.selectbox("Language / اللغة", ["Arabic", "English"], index=0 if current_language() == "Arabic" else 1)
        template = st.selectbox(
            "Template / القالب",
            ["intro", "objectives", "questions", "chapter1", "compare", "gap", "review", "roadmap"],
            format_func=lambda x: {
                "intro": "Introduction / مقدمة الأطروحة",
                "objectives": "Objectives / أهداف البحث",
                "questions": "Research Questions / أسئلة البحث",
                "chapter1": "Chapter 1 Plan / خطة الفصل الأول",
                "compare": "Comparison / المقارنة",
                "gap": "Research Gap / فجوة البحث",
                "review": "Literature Review / مراجعة أدبية",
                "roadmap": "Thesis Roadmap / خطة الأطروحة",
            }[x],
        )

        if selected_titles and st.button(t("generate")):
            generated = generate_text_for_selection(selected_titles, records, template, language_choice)
            st.session_state.generated_text = generated

        if "generated_text" in st.session_state and st.session_state.generated_text:
            st.markdown("### " + t("generated_text"))
            st.write(st.session_state.generated_text)
            if st.button("Save generated text / حفظ النص المولد"):
                add_review(project_id, f"Generated Output - {template}", st.session_state.generated_text)
                st.success("Generated text saved")
                st.rerun()
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
