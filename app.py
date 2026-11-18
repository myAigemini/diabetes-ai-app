import os
from datetime import datetime
import streamlit as st
import pandas as pd
import joblib
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="نظام التشخيص الذكي", page_icon="🩺", layout="centered")

st.markdown("""
<style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    div[class^='viewerBadge'] {display: none !important;}
    div[class*='viewerBadge'] {display: none !important;}
    a[href^="https://streamlit.io/cloud"] {display: none !important;}

    /* تحويل اتجاه التطبيق بالكامل من اليمين إلى اليسار */
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', 'Tahoma', 'Arial', sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 0rem;
        max-width: 850px;
    }

    /* ضبط اتجاه العناوين والحقول والقوائم والرسائل */
    label, p, h1, h2, h3, .stMarkdown, .stAlert,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="select"] > div,
    ul[data-baseweb="menu"] li {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', 'Tahoma', 'Arial', sans-serif !important;
    }

    /* إبقاء شريط السحب LTR حتى يعمل بسلاسة */
    div[data-baseweb="slider"] {
        direction: ltr !important;
    }

    .title {
        text-align: center !important;
        color: #1E3A8A !important;
        padding-bottom: 10px;
    }

    .report-card {
        direction: rtl;
        text-align: right;
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }

    .report-header {
        color: #1E3A8A !important;
        border-bottom: 2px solid #1E3A8A;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }

    .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }

    .report-table td {
        padding: 8px 12px;
        border: 1px solid #e2e8f0;
        font-size: 15px;
        text-align: right;
    }

    .report-table td.label {
        background-color: #eff6ff;
        font-weight: bold;
        color: #1e293b;
        width: 45%;
    }

    .footer {
        text-align: center !important;
        margin-top: 60px;
        padding: 20px;
        font-size: 15px;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='title'>نظام التشخيص الذكي لمرض السكري 🩺</h2>", unsafe_allow_html=True)
st.write("")

@st.cache_resource
def load_model():
    return joblib.load('diabetes_model.pkl')

model = load_model()

# حل مشكلة اختفاء الحروف المنفصلة في الخطوط الحديثة مثل Cairo
reshaper = arabic_reshaper.ArabicReshaper(configuration={
    'use_unshaped_instead_of_isolated': True
})

def ar(text):
    reshaped_text = reshaper.reshape(str(text))
    return get_display(reshaped_text)

def get_arabic_fonts():
    local_fonts = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")
    search_dirs = [".", local_fonts, "C:/Windows/Fonts"]
    
    font_pairs = [
        ("Cairo-Regular.ttf", "Cairo-Bold.ttf"),
        ("Tajawal-Regular.ttf", "Tajawal-Bold.ttf"),
        ("Almarai-Regular.ttf", "Almarai-Bold.ttf"),
        ("Amiri-Regular.ttf", "Amiri-Bold.ttf"),
        ("tahoma.ttf", "tahomabd.ttf"),
        ("arial.ttf", "arialbd.ttf"),
    ]
    
    for reg_name, bold_name in font_pairs:
        for folder in search_dirs:
            if not folder:
                continue
            reg_path = os.path.join(folder, reg_name)
            bold_path = os.path.join(folder, bold_name)
            if os.path.exists(reg_path):
                return reg_path, (bold_path if os.path.exists(bold_path) else reg_path)

    linux_fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(linux_fallback):
        return linux_fallback, linux_fallback
    return None, None

def get_bmi_status(bmi):
    if bmi < 18.5:
        return "نحافة"
    elif bmi < 25:
        return "وزن طبيعي"
    elif bmi < 30:
        return "زيادة في الوزن"
    else:
        return "سمنة"

def generate_pdf(report):
    reg_font, bold_font = get_arabic_fonts()
    if not reg_font:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arabic", "", reg_font)
    pdf.add_font("Arabic", "B", bold_font)

    # ترويسة التقرير
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arabic", "B", size=16)
    pdf.cell(0, 14, ar("تقرير نظام التشخيص الذكي لمرض السكري"), align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # تاريخ ووقت الفحص بنظام 12 ساعة
    if "time_12" in report and "period" in report:
        pdf_date_str = f"{ar(report['period'])} {report['time_12']}  |  {report['date_only']}"
    else:
        pdf_date_str = report["date"]

    pdf.set_text_color(71, 85, 105)
    pdf.set_font("Arabic", "", size=11)
    pdf.cell(95, 8, pdf_date_str, align="L")
    pdf.set_font("Arabic", "B", size=11)
    pdf.cell(95, 8, ar("تاريخ ووقت الفحص:"), align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # عنوان جدول بيانات المريض
    pdf.set_fill_color(226, 232, 240)
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arabic", "B", size=13)
    pdf.cell(0, 10, ar("بيانات المريض والمؤشرات الحيوية"), align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    rows = [
        ("اسم المريض", ar(report["patient_name"])),
        ("الجنس", ar(report["gender"])),
        ("العمر", f"{report['age']}"),
        ("الوزن / الطول", f"{report['weight']} kg  /  {report['height']} cm"),
        ("مؤشر كتلة الجسم (BMI)", f"{report['bmi']:.1f}"),
        ("تصنيف الوزن", ar(report["bmi_status"])),
        ("ارتفاع ضغط الدم", ar(report["hypertension"])),
        ("أمراض القلب", ar(report["heart_disease"])),
        ("حالة التدخين", ar(report["smoking_label"])),
        ("مستوى الجلوكوز في الدم", f"{report['blood_glucose']} mg/dL"),
        ("مستوى السكر التراكمي (HbA1c)", f"{report['hba1c']} %"),
    ]

    pdf.set_draw_color(203, 213, 225)
    for idx, (label, val) in enumerate(rows):
        fill_val = (248, 250, 252) if idx % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*fill_val)
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Arabic", "", size=11)
        pdf.cell(95, 9, str(val), border=1, align="C", fill=True)

        pdf.set_fill_color(239, 246, 255)
        pdf.set_font("Arabic", "B", size=11)
        pdf.cell(95, 9, ar(label), border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    # قسم تقرير الذكاء الاصطناعي
    pdf.set_fill_color(226, 232, 240)
    pdf.set_text_color(30, 58, 138)
    pdf.set_font("Arabic", "B", size=13)
    pdf.cell(0, 10, ar("تقرير ونتيجة الذكاء الاصطناعي"), align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if report["prediction"] == 1:
        pdf.set_fill_color(254, 226, 226)
        pdf.set_text_color(185, 28, 28)
        result_line = "النتيجة: تشير البيانات إلى احتمالية الإصابة بمرض السكري."
        advice_line = "التوصية: يُنصح بمراجعة الطبيب المختص لإجراء الفحوصات السريرية الدقيقة."
    else:
        pdf.set_fill_color(220, 252, 231)
        pdf.set_text_color(21, 128, 61)
        result_line = "النتيجة: المريض سليم بحمد الله، والمؤشرات الحيوية طبيعية."
        advice_line = "التوصية: يُنصح بالحفاظ على نمط حياة صحي ومتابعة الفحوصات الدورية."

    pdf.set_font("Arabic", "B", size=12)
    pdf.cell(0, 10, ar(result_line), border="LTR", align="R", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arabic", "", size=11)
    pdf.cell(0, 10, ar(advice_line), border="LBR", align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # تنبيه طبي وتوقيع المطور
    pdf.set_text_color(100, 116, 139)
    pdf.set_font("Arabic", "", size=9)
    pdf.cell(0, 7, ar("ملاحظة: هذا التقرير ناتج عن نموذج ذكاء اصطناعي لأغراض الفحص المبدئي ولا يُغني عن التشخيص الطبي المباشر."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Arabic", "B", size=10)
    pdf.cell(0, 8, ar("برمجة وتطوير م/ أكرم غالب "), align="C", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())

with st.form("diagnosis_form"):
    patient_name = st.text_input("اسم المريض (اختياري لظهوره في التقرير)", placeholder="مثال: أحمد محمد")

    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        age = st.number_input("العمر", min_value=1, max_value=120, value=30)
        weight = st.number_input("الوزن (كجم)", min_value=10.0, max_value=300.0, value=70.0)
        height = st.number_input("الطول (سم)", min_value=50.0, max_value=250.0, value=170.0)
        
    with col2:
        hypertension = st.selectbox("هل يعاني من ارتفاع ضغط الدم؟", ["لا", "نعم"])
        heart_disease = st.selectbox("هل يعاني من أمراض القلب؟", ["لا", "نعم"])
        smoking_label = st.selectbox("حالة التدخين", [
            "لم أدخن أبداً",
            "لا توجد معلومات",
            "مدخن سابق",
            "غير مدخن حالياً",
            "دخنت في فترة سابقة",
            "مدخن حالياً"
        ])
        blood_glucose = st.number_input("مستوى الجلوكوز في الدم (mg/dL)", min_value=50, max_value=400, value=100)
        
    st.write("---")
    hba1c = st.slider("مستوى السكر التراكمي (HbA1c)", min_value=3.5, max_value=15.0, value=5.5, step=0.1)
    
    submitted = st.form_submit_button("إجراء الفحص وإصدار التقرير", use_container_width=True)

if submitted:
    bmi = weight / ((height / 100) ** 2)
    
    gender_val = 1 if gender == "ذكر" else 0
    hyper_val = 1 if hypertension == "نعم" else 0
    heart_val = 1 if heart_disease == "نعم" else 0
    
    smoking_dict = {
        "لم أدخن أبداً": 0,
        "لا توجد معلومات": 1,
        "مدخن سابق": 2,
        "غير مدخن حالياً": 3,
        "دخنت في فترة سابقة": 4,
        "مدخن حالياً": 5
    }
    smoking_val = smoking_dict[smoking_label]
    
    input_data = pd.DataFrame({
        'gender': [gender_val],
        'age': [age],
        'hypertension': [hyper_val],
        'heart_disease': [heart_val],
        'smoking_history': [smoking_val],
        'bmi': [bmi],
        'HbA1c_level': [hba1c],
        'blood_glucose_level': [blood_glucose]
    })
    
    prediction = int(model.predict(input_data)[0])

    now = datetime.now()
    period = "صباحا" if now.hour < 12 else "مساء"
    date_only = now.strftime('%Y-%m-%d')
    time_12 = now.strftime('%I:%M')

    st.session_state["report"] = {
        "patient_name": patient_name.strip() if patient_name.strip() else "غير محدد",
        "gender": gender,
        "age": age,
        "weight": weight,
        "height": height,
        "bmi": bmi,
        "bmi_status": get_bmi_status(bmi),
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "smoking_label": smoking_label,
        "blood_glucose": blood_glucose,
        "hba1c": hba1c,
        "prediction": prediction,
        "date": f"{date_only} | {time_12} {period}",
        "date_only": date_only,
        "time_12": time_12,
        "period": period
    }

if "report" in st.session_state:
    r = st.session_state["report"]

    st.markdown(f"""
    <div class="report-card">
        <h3 class="report-header">📋 التقرير الطبي المبدئي</h3>
        <p style="color:#475569; font-size:14px;"><b>تاريخ الفحص:</b> {r['date']}</p>
        <table class="report-table">
            <tr><td class="label">اسم المريض</td><td>{r['patient_name']}</td></tr>
            <tr><td class="label">الجنس / العمر</td><td>{r['gender']} - {r['age']} سنة</td></tr>
            <tr><td class="label">الوزن / الطول</td><td>{r['weight']} كجم / {r['height']} سم</td></tr>
            <tr><td class="label">مؤشر كتلة الجسم (BMI)</td><td>{r['bmi']:.1f} ({r['bmi_status']})</td></tr>
            <tr><td class="label">ارتفاع ضغط الدم</td><td>{r['hypertension']}</td></tr>
            <tr><td class="label">أمراض القلب</td><td>{r['heart_disease']}</td></tr>
            <tr><td class="label">حالة التدخين</td><td>{r['smoking_label']}</td></tr>
            <tr><td class="label">مستوى الجلوكوز في الدم</td><td>{r['blood_glucose']} mg/dL</td></tr>
            <tr><td class="label">السكر التراكمي (HbA1c)</td><td>{r['hba1c']}%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if r["prediction"] == 1:
        st.error("⚠️ تقرير الذكاء الاصطناعي: تشير البيانات إلى احتمالية الإصابة بمرض السكري. يُنصح بمراجعة الطبيب المختص لإجراء فحوصات دقيقة.")
    else:
        st.success("✅ تقرير الذكاء الاصطناعي: المريض سليم بحمد الله، المؤشرات الحيوية طبيعية ولا توجد علامات للإصابة.")

    pdf_bytes = generate_pdf(r)
    if pdf_bytes:
        safe_name = r["patient_name"]
        for ch in '\\/*?:"<>|':
            safe_name = safe_name.replace(ch, "")
        safe_name = safe_name.strip().replace(" ", "_")
        file_title = f"تقرير_السكري_{safe_name}.pdf" if safe_name and r["patient_name"] != "غير محدد" else "تقرير_تشخيص_السكري.pdf"
        
        st.download_button(
            label="📥 حفظ التقرير بصيغة PDF لعرضه على الطبيب",
            data=pdf_bytes,
            file_name=file_title,
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("يرجى وضع ملف خط عربي (مثل Cairo-Regular.ttf أو tahoma.ttf) داخل مجلد المشروع لتفعيل تصدير PDF.")

st.markdown("<div class='footer'>برمجة وتطوير م/أكرم غالب </div>", unsafe_allow_html=True)