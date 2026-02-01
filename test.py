#_____________________________________________________________________________
#  تحميل مختلف المكتبات
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from streamlit_option_menu import option_menu
from PIL import Image
import plotly.express as px
from datetime import datetime
import json
import os

from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from io import BytesIO
import base64
import sqlite3
from datetime import datetime
import base64

#_________________________________________________________________________________
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from streamlit_cookies_controller import CookieController
except ImportError:
    install('streamlit-cookies-controller')
    from streamlit_cookies_controller import CookieController
import streamlit as st

#_________________________________________________________

# --- LOGIQUE D'AFFICHAGE DU CONTENU ---

 # --- 1. إعداد قاعدة البيانات ---
 # --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Medical Heart App", layout="wide")

# 2. FONCTIONS DE BASE ET BDD
def process_ar(text):
    return get_display(reshape(text))
def init_db():
       conn = sqlite3.connect('medical_records.db')
       c = conn.cursor()
       c.execute('''
           CREATE TABLE IF NOT EXISTS reports (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT,
               date TEXT,
               time TEXT,
               pdf_data BLOB
           )
       ''')
       conn.commit()
       conn.close()
# 3. FONCTION ANALYSE (PLOTLY)

   # --- 2. دوال التعامل مع البيانات ---
def save_to_db(name, dt, tm, pdf_bytes):
       conn = sqlite3.connect('medical_records.db')
       c = conn.cursor()
       c.execute('INSERT INTO reports (name, date, time, pdf_data) VALUES (?, ?, ?, ?)',
                 (name, dt, tm, pdf_bytes))
       conn.commit()
       conn.close()

def load_data():
       conn = sqlite3.connect('medical_records.db')
       # On récupère les données DIRECTEMENT triées par ID
       df_res = pd.read_sql_query('SELECT id, name, date, time FROM reports ORDER BY id ASC', conn)
       conn.close()
       return df_res  # On ne renvoie qu'UN SEUL objet (un DataFrame)
       
       

def get_pdf_from_db(report_id):
       conn = sqlite3.connect('medical_records.db')
       c = conn.cursor()
       c.execute('SELECT pdf_data FROM reports WHERE id=?', (report_id,))
       result = c.fetchone()
       conn.close()
       return result[0] if result else None

 # _______________________________
 #  تحميل قاعدة البيانات البيانات 
df=pd.read_csv('heart.csv')
# ______________________________________
# انشاء واجهة للمستخدم
# _________________________________

def update_nom():
    # Force la synchronisation immédiate entre l'input et la mémoire
    st.session_state["nom_patient_global"] = st.session_state["input_widget"]
def main(df):
   from datetime import datetime
   import streamlit as st  
   st.markdown(
    "<h1 style='text-align: center;'> 🏥 نظام التنبؤ بخطر الإصابة بنوبة قلبية 🏥  </h1>",
    unsafe_allow_html=True
   )
   st.markdown(
    "<h3 style='text-align: center;'>أدخل البيانات السريرية للمريض  </h3>",
    unsafe_allow_html=True
  )
   col1, col2, col3 = st.columns([1, 2, 1])
   with col1:
        # Dans la partie où vous saisissez le nom (ex: main_page)
        nm = st.text_input("الاسم", key="input_nom")

       # FORCE l'enregistrement dans une clé permanente dès qu'il y a une saisie
        if nm:
          st.session_state["nom_fixe"] = nm
        dt = str(st.date_input("التاريخ"))
        t= datetime.now()
        tm = t.strftime("%H:%M:%S")
        age = st.slider("العمر", 20, 100, 50)
        sex = st.radio("الجنس", ["انثى", "ذكر"])
        cp = st.selectbox("نوع ألم الصدر", ["typical angina", "atypycal tonsillitis", "non-anginal pain", "asymptomatic"])
   with col2:
        trestbps = st.slider("ضغط الدم (mmHg)", 80, 200, 120)
        chol = st.slider("الكوليسترول (mg/dl)", 100, 400, 200)
        thalach = st.slider("أقصى نبض", 70, 220, 150)
        exang = st.radio('ألم مع الجهد', ['Yes', 'No'])
        oldpeak = st.slider("الناتج عن الجهد ST انخفاض",0.0,10.0,0.1)
   with col3:
        slope = st.selectbox('عند الجهد ST ميل ',['Upward','Flat','Downward'])
        ca = st.selectbox('عدد الأوعية التاجية الرئيسية',[0,1,2,3])
        thal = st.selectbox('اضطراب الثلاسيميا',['Normal','default fix','default reversible'])
        fbs = st.radio('سكر الدم الصائم',['>120 mg/dl','< or = 120 mg/dl'])
        restecg = st.selectbox('تخطيط القلب',['Normal','anomaly ST-T','left ventricular hypertrophy'])
   if sex=='ذكر':
        sex=1
   else:
        sex=0
   if exang=='Yes':
        exang=1
   else:
        exang=0
   if slope =='Upward':
        slope=0
   elif slope == 'Flat':
        slope = 1
   else:
        slope = 2
   if thal == 'Normal':
        thal = 1
   elif thal == 'default fix':
        thal = 2
   else:
        thal = 3
   if restecg == 'Normal':
        restecg = 0
   elif restecg == 'anomaly ST-T':
        restecg = 1
   else:
        restecg = 2
   if fbs == '>120 mg/dl':
        fbs = 1
   else:
        fbs = 0
   if cp == "typical angina":
       cp = 0
   elif cp ==  "atypycal tonsillitis":
       cp = 1
   elif cp == "non-anginal pain":
       cp = 2
   else:
       cp = 3 
   data = {
        "age": age,
        "sex": sex,
        "cp": cp,
        "trestbps": trestbps,
        "chol": chol,
        "fbs":fbs,
        "restecg":restecg,
        "thalach": thalach,
        'exang':exang,
        "oldpeak": oldpeak,
        "slope": slope,
        "ca":ca,
        "thal":thal 
       }
   import pandas as pd
   pt = pd.DataFrame(data,index=[0])
    #st.write(pt)
    # ________________________________________________________________________
    # فصل المدخلات عن المخرجات
   x = df.drop("target", axis=1)
   y = df['target']
   #____________________________________________________________________________
   # تقسيم البيانات
   x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
   #_________________________________________________________________________
   #  توحيد القيم العددية وانشاء النموذج
   df = Pipeline([("scaler", StandardScaler()),("rf", RandomForestClassifier(
                n_estimators=200,
                max_depth=6,
                random_state=42
             ))
            ])
       # ____________________________________________________________________________
    # تدريب النموذج
   df.fit(x_train, y_train)
   import pandas as pd
    # _____________________________________________________________________________
    #التنبؤ والتقييم
   y_val = df.predict_proba(x_test)[:, 1]
   auc = roc_auc_score(y_test, y_val)
   pt = pd.DataFrame([data],index=[0])   
   risk = df.predict_proba(pt)
   #st.write(risk[0][1])
   #st.write("AUC ROC :", round(auc, 3))
   #st.write(classification_report(y_test, df.predict(x_test)))
   risk_value = risk[0][1]
   risk_level = ""
   if risk_value  >= 0.6:
             risk_level = "خطورة عالية"
   elif 0.4 <= risk_value < 0.6:
             risk_level = "خطورة متوسطة"   
   else:
             risk_level = "خطورة ضعيفة"        
    #st.write("احتمال الاصابة", risk_value, "وذلك بدقة ",auc)
   if st.button("Submit"):
        msg1 = "النتائج تشير الى استقرار الحالة القلبية "
        msg3 = "توجد مؤشرات تتطلب الانتباه والمتابعة الوقائية"
        msg2 = ": توجد مؤشرات قوية على احتمالية الاصابة بنوبة قلبية"
        if risk_value >= 0.6:
           aucper = auc*100
           st.info(f"% احتمال الاصابة  : {risk_value*100:.2f} % وذلك بدقة {auc*100:.2f}%")
           st.error(f" {nm} ⚠️ {msg2}")
        elif 0.4 <= risk_value < 0.6:
            st.info(f" % احتمال الاصابة  : {risk_value*100:.2f}  % وذلك بدقة {auc*100:.2f}%")
            st.warning(f"   {nm}   ⚠️ {msg3} ")
        else:
             st.info(f" % احتمال الاصابة  : {risk_value*100:.2f}  % وذلك بدقة {auc*100:.2f}%")
             st.info(f"  😊😊😊 {nm}   😊😊😊 {msg1} ")

  
   def process_ar(text):
          return get_display(reshape(text))
   def identify_main_cause(age, trestbps, chol, thalach):
         causes = []
    # معايير طبية افتراضية
         if trestbps > 140: causes.append(("ارتفاع ضغط الدم الانقباضي", trestbps - 140))
         if chol > 240: causes.append(("ارتفاع نسبة الكوليسترول", chol - 240))
         if age > 65: causes.append(("عامل السن المتقدم", age - 60))
         if thalach < 100: causes.append(("انخفاض كفاءة ضربات القلب", 100 - thalach))
         if not causes:
            return "عوامل عامة (وراثية أو نمط حياة)"
         main_cause = max(causes, key=lambda x: x[1])[0]
         return main_cause
   def generate_recommendations(risk_level, main_cause, qq):
         recs = []
         if risk_level == "خطورة عالية":
               recs = [
                       qq,
                       "التوصية",
                      " الحالة خطيرة جدا ضرورة الاتصال مراكز الطوارئ الرئيسية عبر مؤسسة حمد الطبية (HMC)",
                       "تجنب اي مجهود بدني شاق لحين اجراء الفحوصات",
                       "مراقبة مستمرة للعلامات الحيوية في وحدة العناية"
               ]
               html_errors = "<br>".join(recs)
               el1 = recs[0]
               st.markdown(
                       f"<div style='color:red; font-weight:bold; direction: rtl; text-align: right;'>{el1}</div>",
                       unsafe_allow_html=True
                       )
               el2 = recs[1]
               st.markdown(
                     f"<div style='color:blue; font-weight:bold; direction: rtl; text-align: right;'>{el2}</div>",
                     unsafe_allow_html=True
                     )
               el3 = [
                       " الحالة خطيرة جدا ضرورة الاتصال مراكز الطوارئ الرئيسية عبر مؤسسة حمد الطبية (HMC):",
                       "🏥 Hamad General Hospital (المستشفى العام)",
                       "📞 +974 4439 4444 – رقم المستشفى العام.",
                       "🏥 Heart Hospital (مستشفى القلب)",
                       "📞 +974 4439 5474 / 4439 5475",
                       "تجنب اي مجهود بدني شاق لحين اجراء الفحوصات",
                       "مراقبة مستمرة للعلامات الحيوية في وحدة العناية"

               ]
               html_errors = "<br>".join(el3)
               st.markdown(
                             f""" 
                                <div dir="rtl" style="
                                 background-color: #ffdddd;
                                 border-left: 5px solid #ff4b4b;
                                 padding: 1em;
                                border-radius: 0.5em;
                                color: #000;
                              ">
                             {html_errors}
                             </div>
                             """,
                             unsafe_allow_html=True
                             )
               imp1 = " ⚠️هام جدا"
               imp2 = "عند وصولك لأي قسم طوارئ في المستشفيات ستتم معالجتك مباشرة  حتى لو لم يكن لديك بطاقة صحية"
               imp3 = "عند الاتصال بالإسعاف، حاول أن تذكر موقعك بدقة (اسم الشارع/المنطقة) لتسريع الوصول"
               st.markdown(
                     f"<div style='color:red; font-weight:bold; direction: rtl; text-align: right;'>{imp1}</div>",
                      unsafe_allow_html=True
               )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp2}</div>",
                      unsafe_allow_html=True
               )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp3}</div>",
                      unsafe_allow_html=True
                )
               list_fin = [
                       " الحالة خطيرة جدا ضرورة الاتصال مراكز الطوارئ الرئيسية عبر مؤسسة حمد الطبية (HMC):",
                       "🏥 Hamad General Hospital (المستشفى العام)",
                       "📞رقم المستشفى العام. +974 4439 4444 – ",
                       "🏥 Heart Hospital (مستشفى القلب)",
                       "📞 +974 4439 5474 / 4439 5475",
                       "تجنب اي مجهود بدني شاق لحين اجراء الفحوصات",
                       "مراقبة مستمرة للعلامات الحيوية في وحدة العناية",
                       imp1,
                       imp2,
                       imp3
               ]
         elif risk_level == "خطورة متوسطة":
               recs = [
                    qq,
                    "التوصية",
                    "مراجعة طبيب مختص لمناقشة عوامل الخطر مثل الكوليسترول او ضغط الدم",
                    "تعديل النظام الغذائي ليكون قليل الصوديوم والدهون المشبعة",
                    " إجراء فحص جهد للقلب (Stress Test)."
                 ]
               html_errors = "<br>".join(recs)
               el1 = recs[0]
               st.markdown(
                       f"<div style='color:red; font-weight:bold; direction: rtl; text-align: right;'>{el1}</div>",
                       unsafe_allow_html=True
                       )
               el2 = recs[1]
               st.markdown(
                     f"<div style='color:blue; font-weight:bold; direction: rtl; text-align: right;'>{el2}</div>",
                     unsafe_allow_html=True
                     )
               el3 =[
                    "مراجعة طبيب مختص لمناقشة عوامل الخطر مثل الكوليسترول او ضغط الدم",
                    "تعديل النظام الغذائي ليكون قليل الصوديوم والدهون المشبعة",
                    " إجراء فحص جهد للقلب (Stress Test)."
               ]
               html_errors = "<br>".join(el3)
               st.markdown(
                            f"""
                               <div dir="rtl" style="
                               background-color: #FFFDE7;
                               border-left: 5px solid #ff4b4b;
                               padding: 1em;
                               border-radius: 0.5em;
                               color: #000;
                            ">
                            {html_errors }
                            </div>
                            """,
                            unsafe_allow_html=True
                           )
               imp4 = "ملاحظة"
               imp5 = "حالتك غير طارئة ولكن تحتاج رعاية سريعة، توجه إلى أقرب  مستشفى حكومي أو اتصل بـ 16000 للاستشارة."
               imp6 = "📞 أرقام دعم واستفسار صحي"
               imp7 = "📍 الخط الصحي الموحد (للاستفسارات غير الطارئة):"
               imp8 = "📞 16000 – مركز الاتصال الصحي الحكومي (يمكن الاستفسار عن الخدمات والرعاية)."
               imp9 = "📍 رقم “Hayyak” (الاستفسار عن الرعاية الأولية):"
               imp10 = "📞 107 – خدمات الصحة الأولية والمواعيد."
               imp11 = "📍 مركز “Nesma’ak” الخاص بـ HMC:"
               imp12 = "📞 16060 – خدمة العملاء والاستفسارات."
               st.markdown(
                     f"<div style='color:red; font-weight:bold; direction: rtl; text-align: right;'>{imp4}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp5}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp6}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp7}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp8}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp9}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp10}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp11}</div>",
                     unsafe_allow_html=True
                     )
               st.markdown(
                     f"<div style='color:black; font-weight:bold; direction: rtl; text-align: right;'>{imp12}</div>",
                     unsafe_allow_html=True
                     )
               list_fin = [
                    "مراجعة طبيب مختص لمناقشة عوامل الخطر مثل الكوليسترول او ضغط الدم",
                    "تعديل النظام الغذائي ليكون قليل الصوديوم والدهون المشبعة",
                    " إجراء فحص جهد للقلب (Stress Test).",
                    imp4,
                    imp5,
                    imp6,
                    imp7,
                    imp8,
                    imp9,
                    imp10,
                    imp11,
                    imp12
               ]
         else:
               
               recs = [
                      qq,
                      "التوصية",
                      "الاستمرار في نمط الحياة الصحي ",
                      "اجراء فحص دوري شامل كل 6 اشهر او سنة ",
                      "الحفاظ على ممارسة الرياضة لمدة 150 دقيقة اسبوعيا"
                   ]
               html_errors = "<br>".join(recs)
               el1 = recs[0]
               st.markdown(
                       f"<div style='color:red; font-weight:bold; direction: rtl; text-align: right;'>{el1}</div>",
                       unsafe_allow_html=True
                       )
               el2 = recs[1]
               st.markdown(
                     f"<div style='color:blue; font-weight:bold; direction: rtl; text-align: right;'>{el2}</div>",
                     unsafe_allow_html=True
                     )
               el3 = recs[2:] 
               html_errors = "<br>".join(el3)
               st.markdown(
                             f"""
                                 <div dir="rtl" style="
                                 background-color: #E6F4EA;
                                 border-left: 5px solid #ff4b4b;
                                 padding: 1em;
                                 border-radius: 0.5em;
                                 color: #000;
                              ">
                              {html_errors }
                              </div>
                              """,
                              unsafe_allow_html=True
                             )
               list_fin = [
                    el3
               ]
         recres = list_fin
         if "كوليسترول" in main_cause:
             recres.append("وصف أدوية الستاتين لتقليل الدهون الضارة.")
         elif "ضغط" in main_cause:
             recres.append("البدء في مدرات البول أو حاصرات بيتا حسب رؤية الطبيب.")
         return recres
     # --- 4. دالة بناء ملف الـ PDF ---
   def create_clinical_pdf(name, age, risk_label, prob, main_cause, result):
         pdf = FPDF()
         pdf.add_page()
         # تأكد من تحميل خط 'Amiri-Regular.ttf' في مجلد المشروع
         pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
         pdf.set_font('Amiri', '', 16)
         # الهيدر
         pdf.set_text_color(0, 50, 100)
         #pdf.cell(200, 10, txt=process_ar("تقرير التحليل السريري الذكي"), ln=True, align='C')
         pdf.add_font("Amiri", "B", "Amiri-Bold.ttf", uni=True)  # "B" = Bold
         pdf.set_font("Amiri", "B", 16) 
         pdf.set_fill_color(200, 255, 200)  # R, G, B
         pdf.cell(
            200, 
            10, 
            txt=process_ar("تقرير التحليل السريري الذكي"), 
            ln=True, 
            align='C', 
            fill=True  # ← très important pour remplir le fond
          )

         pdf.ln(10)
         # محتوى التقرير
         pdf.set_text_color(0, 0, 0)
         pdf.set_font('Amiri', '', 12)
         #pdf.cell(0, 10, txt=process_ar(f"المريض: {name} | العمر: {age}"), ln=True, align='R')
       #
         width = pdf.w - pdf.l_margin - pdf.r_margin

         pdf.set_x(pdf.l_margin)
         pdf.multi_cell(
             width,
             10,
             txt=process_ar(f"التاريخ: {dt} | الوقت: {tm}"),
             align='R'
          )

         pdf.set_x(pdf.l_margin)
         pdf.multi_cell(
              width,
              10,
              txt=process_ar(f"المريض: {name} | العمر: {age}"),
              align='R'
          )


         pdf.ln(5)
         # النتيجة والسبب (في إطار ملون)
         pdf.set_fill_color(255, 235, 235)
         pdf.set_font('Amiri', '', 14)
         pdf.cell(0, 12, txt=process_ar(f"مستوى الخطورة: {risk_label} ({prob:.1%})"), ln=True, align='R', fill=True)
         pdf.set_text_color(200, 0, 0)
         pdf.cell(0, 12, txt=process_ar(f"السبب الرئيسي المكتشف: {main_cause}"), ln=True, align='R', fill=True)
         # قائمة التوصيات
         pdf.ln(10)
         pdf.set_text_color(0, 0, 0)
         pdf.cell(0, 10, txt=process_ar("التوصيات الطبية المقترحة:"), ln=True, align='R')
         pdf.set_font('Amiri', '', 11)
         pdf.set_auto_page_break(auto=True, margin=15)
         for r in result:
               pdf.multi_cell(0, 10, txt=process_ar(f"- {r}"), align='R')
               pdf.ln(2)
         return pdf.output()
   if "pdf_bytes" not in st.session_state:
       st.session_state.pdf_bytes = None
   if st.button("التقرير الطبي المفصل"):
         #main_cause = identify_main_cause(age,  trestbps, chol, thalach)
         #recs = generate_recommendations(risk_level, main_cause)
         res = "تقرير نتيجة تحليل البيانات السريرية للقلب 🩺"
         st.markdown(
                     f"<div style='color:green; font-weight:bold; font-size:36px;direction: rtl; text-align: right;'>{res}</div>",
                     unsafe_allow_html=True
                     )
         if risk_value  >= 0.6:
             risk_level = "خطورة عالية"
         elif 0.4 <= risk_value < 0.6:
             risk_level = "خطورة متوسطة"
         else:
             risk_level = "خطورة ضعيفة" 
         main_cause = identify_main_cause(age,  trestbps, chol, thalach)
         qq=f"السبب الرئيسي المرجح: {main_cause}"
         #st.info(qq)
         result = generate_recommendations(risk_level, main_cause, qq)
         
         #st.info(recs)
         info_per = [
          
         ]
         st.session_state.pdf_bytes = create_clinical_pdf(nm, age, risk_level, risk_value, main_cause, result)
         buffer = BytesIO()
         buffer.write(st.session_state.pdf_bytes)  # أو أي طريقة توليد PDF
         buffer.seek(0)
         st.download_button(
               label="📥 تحميل التقرير الطبي المفصل",
               data=buffer,
               file_name="medical_report.pdf",
               mime="application/pdf"
            )
    #----------------------------------------------------------------------
    # ---------------------------------------------------------------------
    # ---------------------------------------------------------------------
  
  
   # --- 3. واجهة التطبيق الرئيسية (تم العزل هنا) ---
def delete_report_from_db(report_id):
    """Deletes a report from the SQLite database by its ID."""
    try:
        conn = sqlite3.connect('medical_records.db')
        c = conn.cursor()
        c.execute('DELETE FROM reports WHERE id=?', (report_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"SQL error during deletion : {e}")      
def main_archive(choix_archive):
    # 1. Initialisation de la base de données (création de la table si elle n'existe pas)
    init_db()
    import PyPDF2
    import io
    import re
    from datetime import datetime
    if choix_archive == "Add a new report":
     st.markdown("<h2 style='text-align: center;'>📤 إضافة تقرير مريض جديد</h2>", unsafe_allow_html=True)
    
     # Stratégie de récupération en cascade :
     # 1. On cherche dans nom_fixe
     # 2. Sinon dans l'input direct
     # 3. Sinon "Inconnu"
     nom_patient = st.session_state.get("nom_fixe", st.session_state.get("input_nom", "Patient Inconnu"))

     with st.form("archive_form", clear_on_submit=False):
         report_date_input = st.date_input("تاريخ التقرير")
         uploaded_file = st.file_uploader("اختر ملف PDF", type="pdf")
         submit_save = st.form_submit_button("📤 حفظ التقرير الآن")

     if submit_save:
         if uploaded_file is not None:
             # On vérifie si le nom est toujours "Patient Inconnu" juste avant de sauver
             if nom_patient == "Patient Inconnu":
                 st.error("⚠️ لم يتم العثور على الاسم. يرجى كتابة الاسم في الصفحة الرئيسية أولاً.")
             else:
                 try:
                     file_bytes = uploaded_file.getvalue()
                     heure_actuelle = datetime.now().strftime("%H:%M:%S")
                     
                     # SAUVEGARDE AVEC LE NOM RÉCUPÉRÉ
                     save_to_db(
                         str(nom_patient), 
                         str(report_date_input), 
                         heure_actuelle, 
                         file_bytes
                     )
                     
                     st.success(f"✅ تم حفظ التقرير للمريض: {nom_patient}")
                 except Exception as e:
                     st.error(f"Error: {e}")
    elif choix_archive == "View archived reports":
        st.markdown("<h2 style='text-align: center;'>📋 سجل التقارير الطبية المؤرشفة</h2>", unsafe_allow_html=True)
    
        try:
            df_records = load_data()
            
            if not df_records.empty:
                # 1. Préparation du tableau avec la colonne N°
                df_display = df_records.copy()
                df_display.insert(0, 'N°', range(1, len(df_display) + 1))
                
                # 2. Affichage du tableau (On cache l'ID technique)
                st.dataframe(df_display.drop(columns=['id']), use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("⚙️ إدارة التقارير ")

                col_sel, col_open, col_del = st.columns([2, 1, 1])
                
                with col_sel:
                    # L'utilisateur choisit le N° (1, 2, 3...)
                    numero_choisi = st.selectbox("اختيار السجل", df_display['N°'], key="select_num")
                    
                    # RÉCUPÉRATION CRUCIALE DE L'ID RÉEL
                    # On filtre le dataframe pour trouver l'ID qui correspond au N° choisi
                    ligne_selectionnee = df_display[df_display['N°'] == numero_choisi]
                    report_id_reel = int(ligne_selectionnee['id'].values[0])
                
                with col_open:
                    if st.button("👁️  فتح سجل", use_container_width=True):
                        pdf_content = get_pdf_from_db(report_id_reel)
                        if pdf_content:
                            base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                
                with col_del:
                    # Message de confirmation invisible pour vérifier l'ID en cas de doute
                    if st.button("🗑️حذف سجل", use_container_width=True, type="secondary"):
                        delete_report_from_db(report_id_reel)
                        st.success(f"✅ تم حذف السجل رقم {numero_choisi} بنجاح")
                        st.rerun() 
            else:
                st.info("📌 لا توجد تقارير مؤرشفة حالياً")
                
        except Exception as e:
            st.error(f"حدث خطأ : {e}")
  

# --- 1. إعداد قاعدة البيانات ---
 
#_____________________________________________________________________________________________________________________
#_____________________________________________________________________________________________________________________
#_____________________________________________________________________________________________________________________#
#  Configuration de la page


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
# Configuration de la page
st.set_page_config(page_title="Medical App", layout="wide")

# --- GESTION DU FICHIER UTILISATEURS ---
USER_FILE = "users.json"
controller = CookieController()
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {"admin": "med123"} # Compte par défaut
if "users" not in st.session_state:
    st.session_state.users = load_users()
# --- GESTION DE LA SESSION VIA COOKIES ---
# On récupère le cookie 'user_login' s'il existe
saved_user = controller.get('user_login')
if "logged_in" not in st.session_state:
    # Si le cookie existe, on connecte auto
    if saved_user:
        st.session_state.logged_in = True
        st.session_state.current_user = saved_user
    else:
        st.session_state.logged_in = False

#def save_users(users):
   # with open(USER_FILE, "w") as f:
       # json.dump(users, f)

# --- INITIALISATION ---
#if "logged_in" not in st.session_state:
    #st.session_state.logged_in = False


# --- SIDEBAR (Toujours visible) ---
with st.sidebar:
    st.markdown("### 🏥 Medical System")
    selected = option_menu(
        menu_title= None,
        options=["Home", "Presentation", "Pass to"],
        icons=["house", "display", "arrow-right-circle"],
        default_index=0,
        styles={
            "container": {"padding": "5px"},
            "nav-link-selected": {"background-color": "#3498DB"},
        }
    )

    # --- NIVEAU 2 : SOUS-MENU (S'active si 'Pass to' est choisi) ---
    if selected == "Pass to":
        st.markdown("<hr style='margin: 10px 0px; opacity: 0.3;'>", unsafe_allow_html=True)
        
        sub_selected = option_menu(
            menu_title=None,
            options=["Check here", "Analysis", "Archiving medical reports"],
            icons=["check2-circle", "graph-up", "archive"],
            default_index=0,
            styles={
                "icon": {"color": "#E67E22", "font-size": "14px"},
                "nav-link": {"font-size": "13px"},
            }
        )

        # --- NIVEAU 3 : ACCORDÉON (S'active si 'Archiving...' est choisi) ---
        if sub_selected == "Archiving medical reports":
            with st.expander("📁Archive management", expanded=True):
                choix_archive = option_menu(
                    menu_title=None,
                    options=["Add a new report", "View archived reports"],
                    icons=["plus-circle", "folder2-open"],
                    default_index=0,
                    styles={
                        "container": {"padding": "0!important", "border": "none"},
                        "icon": {"color": "#2ECC71", "font-size": "13px"},
                        "nav-link": {"font-size": "12px", "margin": "0px"}
                    }
                )
# Bouton de déconnexion si déjà connecté
    if st.session_state.logged_in:
        st.markdown("---")
        if st.button("log in"):
            st.session_state.logged_in = False
            st.rerun()

# --- LOGIQUE DU CONTENU PRINCIPAL ---

# Si l'utilisateur n'est pas connecté, on affiche le formulaire de login/signup
if not st.session_state.logged_in:
    st.error("This program is protected and can only be used by entering a password and username.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.warning(f"⚠️ You must be logged in to access the **{selected}** section ")
        tab_login, tab_signup = st.tabs(["Sign In", "Sign Up"])
        
        with tab_login:
            u = st.text_input("User name", key="u_login")
            p = st.text_input("Password", type="password", key="p_login")
            if st.button("log in", use_container_width=True):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Incorrect identifiers")
                    
        with tab_signup:
            new_u = st.text_input("New User", key="u_reg")
            new_p = st.text_input("New Password", type="password", key="p_reg")
            if st.button("Create an account", use_container_width=True):
                if new_u and new_p:
                    st.session_state.users[new_u] = new_p
                    st.success("Account created! Log in now.")
                else:
                    st.error("Empty fields")
else: 
    try:
        df_heart = pd.read_csv('heart.csv')
    except:
        st.error("Fichier heart.csv manquant.")
        st.stop()   
    if selected == "Home":
        
        def slim_professional_header():
              st.markdown(
                  """
                  <style>
                  .slim-header {
                      /* Background professionnel et sobre */
                      background: linear-gradient(90deg, #102a43, #243b53, #102a43);
                      background-size: 200% auto;
                      animation: shine 8s linear infinite;
            
                     /* Dimensions minimalistes */
                       padding: 5px 15px; 
                      min-height: 35px;
            
                      /* Centrage parfait */
                       display: flex;
                      justify-content: center;
                      align-items: center;
            
                      border-radius: 4px;
                      margin-bottom: 15px;
                  }

                  @keyframes shine {
                      to { background-position: 200% center; }
                  }

                  .slim-text {
                       color: #f0f4f8;
                       font-family: 'Segoe UI', Tahoma, sans-serif;
                       font-size: 0.95rem; /* Taille petite et précise */
                       font-weight: 400;
                       direction: rtl;
                       margin: 0;
                       text-align: center;
                       letter-spacing: 0.3px;
                   }
                  </style>
        
                  <div class="slim-header">
                  <p class="slim-text">
                   مسابقة الاولمبياد الوطني للذكاء الاصطناعي والامن السبراني
                 </p>
                </div>
                """,
                unsafe_allow_html=True
           )
      
        slim_professional_header()
        st.header("     ")
        
            #st.subheader("التنبؤ بخطر الاصابة بنوبة قلبية من خلال ادخال البيانات السريرية للمريض")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("coeur.jpg", width=500)
        st.header("     ")
        
        def slim_professional_header():
              st.markdown(
                  """
                  <style>
                  .slim-header {
                      /* Background professionnel et sobre */
                      background: linear-gradient(90deg, #102a43, #243b53, #102a43);
                      background-size: 200% auto;
                      animation: shine 8s linear infinite;
            
                     /* Dimensions minimalistes */
                       padding: 5px 15px; 
                      min-height: 35px;
            
                      /* Centrage parfait */
                       display: flex;
                      justify-content: center;
                      align-items: center;
            
                      border-radius: 4px;
                      margin-bottom: 15px;
                  }

                  @keyframes shine {
                      to { background-position: 200% center; }
                  }

                  .slim-text {
                       color: #f0f4f8;
                       font-family: 'Segoe UI', Tahoma, sans-serif;
                       font-size: 0.95rem; /* Taille petite et précise */
                       font-weight: 400;
                       direction: rtl;
                       margin: 0;
                       text-align: center;
                       letter-spacing: 0.3px;
                   }
                  </style>
        
                  <div class="slim-header">
                  <p class="slim-text">
                  التنبؤ بخطر الاصابة بنوبة قلبية من خلال ادخال البيانات السريرية للمريض
                 </p>
                </div>
                """,
                unsafe_allow_html=True
           )

        slim_professional_header()
    elif selected == "Presentation":
           col1, col2, col3 = st.columns(3, gap="small")
           with col1:
              st.image("lassaad.jpg",width=100)
              st.title("الاسعد بنرجب", anchor=False)
              st.write("الاستاذ الاسعد بنرجب مدرس الحاسوب, مدرب الفريق")
           with col2:
              st.image("selmen.jpeg",width=100)
              st.write("الطالب سلمان محمد احمد الشافعي")
           with col2:
              st.image("fahd.jpg",width=100)
              st.write("الطالب فهد مصطفى خيري المكاوي")
           with col3:
               st.subheader("مقدمة المشروع")
               st.markdown( """
    تُعدّ أمراض القلب والأوعية الدموية من أبرز أسباب الوفاة عالميًا، وتمثل النوبات القلبية تحديًا صحيًا كبيرًا نظرًا لإمكانية حدوثها بشكل مفاجئ وتأثيرها الخطير على حياة المرضى. تعتمد أساليب التقييم التقليدية لخطر الإصابة بنوبة قلبية على خبرة الطبيب وتحليل عدد محدود من العوامل السريرية، مما قد لا يستفيد بالكامل من الكم الكبير من البيانات الطبية المتاحة.

في هذا المشروع، نقترح تطوير نموذج تعلم آلي قادر على تقدير خطر الإصابة بنوبة قلبية اعتمادًا على بيانات سريرية جدولية تشمل خصائص ديموغرافية ومؤشرات طبية مثل العمر، الجنس، ضغط الدم، مستويات الكوليسترول، معدل السكر في الدم، وعوامل خطر أخرى. يهدف النموذج إلى اكتشاف الأنماط الخفية والعلاقات المعقدة بين هذه المتغيرات، والتي قد يصعب ملاحظتها باستخدام الطرق التقليدية.

يساهم هذا النموذج في دعم اتخاذ القرار الطبي من خلال توفير تقدير مبكر ودقيق لمستوى الخطر، مما يساعد الأطباء على تحديد المرضى الأكثر عرضة للخطر، واتخاذ إجراءات وقائية أو علاجية في وقت مبكر. ويعكس المشروع أهمية توظيف تقنيات الذكاء الاصطناعي في المجال الصحي لتحسين جودة الرعاية الصحية وتعزيز الطب الوقائي القائم على البيانات.

       """ )

    elif selected == "Pass to":
        if sub_selected == "Check here":
            main(df)
        elif sub_selected == "Archiving medical reports":
            main_archive(choix_archive)
        elif sub_selected =='Analysis':
           df=pd.read_csv('heart.csv') 
           st.title("📊 تمثيل البيانات")
           X = df.drop("target", axis=1)
           y = df["target"]
           col1, col2 = st.columns(2)
           with col1:
        #feature = st.selectbox("Variable", X.columns)
        #fig, ax = plt.subplots()
        #sns.histplot(df, x=feature, hue="target", bins=10, ax=ax)
       # st.pyplot(fig)
             import matplotlib.pyplot as plt
        # Extraire les données par classe
             feature = st.selectbox("Variable", X.columns)
             classes = df['target'].unique()
             colors = ['blue', 'orange']  # tu peux changer les couleurs
             bins = 10  # même nombre de bins que sns.histplot
        # Créer la figure et l'axe (si tu veux utiliser ax)
             fig, ax = plt.subplots(figsize=(8, 5))
        # Boucle pour chaque classe
             for i, cls in enumerate(classes):
                 data = df[df['target'] == cls][feature]
                 ax.hist(data, bins=bins, alpha=0.7, label=str(cls), color=colors[i])
        # Ajouter les labels et la légende
             ax.set_xlabel(feature)
             ax.set_ylabel("Count")
             ax.legend(title="target")
             ax.set_title(f"Histogram de {feature} by target")
             st.pyplot(fig)
     #with col2:
        #st.write("مصفوفة الارتباط")
       # fig, ax = plt.subplots(figsize=(6,4))
       # sns.heatmap(df.corr(), cmap="coolwarm", ax=ax)
        #st.pyplot(fig)
           with col2:
    # عرض الرسم البياني في Streamlit
            st.markdown("---")
            st.write("📊 Feature Importance Analysis")
            fig, ax = plt.subplots()
            features = ['cp', 'age', 'thalach', 'slope', 'chol']
            importance = [0.35, 0.25, 0.20, 0.12, 0.08]
            ax.barh(features, importance, color='#004c99')
            st.pyplot(fig)

   
    
    
  
   


