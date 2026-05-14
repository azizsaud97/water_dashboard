from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import io

app = Flask(__name__)
# تفعيل CORS للسماح للواجهة بالتواصل مع السيرفر
CORS(app)

EXCEL_FILE = "marafiq_real_data.xlsx"

# ══════════════════════════════════════════════════════
# تحميل وتنظيف البيانات
# ══════════════════════════════════════════════════════
def load_and_clean_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # تحويل الفراغات عشان ما تسبب مشاكل للموقع
        df = df.replace({np.nan: None})
        
        cleaned_data = []
        for index, row in df.iterrows():
            # قراءة الإحداثيات المنفصلة
            try:
                lat = float(row.get('Y')) if row.get('Y') else None
                lng = float(row.get('X')) if row.get('X') else None
            except:
                lat, lng = None, None
            
            # استخراج اسم المحلة من العنوان (مثل A1)
            address = str(row.get('Address', ''))
            sector = address.split(' ')[0] if address else "غير محدد"
            district = sector[0] if len(sector) > 0 else "?"

            status = str(row.get('Meter Status', ''))
            if status == "غير مفصول وغير موثق":
                status = "غير محدد"

            cleaned_data.append({
                "contract_account": row.get('Contract Account'),
                "account_det": row.get('Account Determination'),
                "zone_type": row.get('Account Determination'), # ضروري للفلتر (سكني، تجاري..)
                "authenticated": row.get('Meter Authenticated'),
                "phone": row.get('Tel No.'),
                "address": address,
                "district": district,
                "sector": sector,
                "lat": lat,
                "lng": lng,
                "average_12m": row.get('Average Last 12 Months'),
                "status": status,
                "zero_consumption": row.get('Zero Consumption'),
                "disc_consumption": row.get('Disconnected and Consumption')
            })
            
        return pd.DataFrame(cleaned_data)
    except Exception as e:
        print(f"❌ خطأ في قراءة الإكسل: {e}")
        return pd.DataFrame()

# تحميل البيانات في الذاكرة مرة واحدة عند التشغيل لزيادة السرعة
global_df = load_and_clean_data()

# ══════════════════════════════════════════════════════
# الروابط (APIs)
# ══════════════════════════════════════════════════════

@app.route('/')
def home():
    if not os.path.exists('dashboard.html'):
        return "❌ ملف dashboard.html غير موجود!", 404
    return send_file('dashboard.html')

@app.route('/api/data', methods=['GET'])
def get_all_data():
    if global_df.empty:
        return jsonify([])
    # إرسال البيانات اللي فيها إحداثيات صحيحة بس
    valid_data = global_df.dropna(subset=['lat', 'lng'])
    return jsonify(valid_data.to_dict(orient='records'))

@app.route('/api/search/<query>', methods=['GET'])
def search_subscriber(query):
    if global_df.empty:
        return jsonify({"error": "No data"})
    
    # البحث باستخدام رقم الحساب أو رقم الجوال
    match = global_df[
        (global_df['contract_account'].astype(str) == str(query)) |
        (global_df['phone'].astype(str) == str(query))
    ]
    
    if not match.empty:
        return jsonify(match.iloc[0].to_dict())
    return jsonify({"error": "Not found"})

@app.route('/api/export', methods=['GET'])
def export_excel():
    if global_df.empty:
        return "لا توجد بيانات", 404
        
    sector_filter = request.args.get('sector', 'all')
    export_df = global_df.copy()
    if sector_filter != 'all':
        export_df = export_df[export_df['sector'] == sector_filter]

    # إرجاع الأسماء كما كانت في الإكسل الأصلي
    export_df = export_df.rename(columns={
        "contract_account": "Contract Account",
        "account_det": "Account Determination",
        "authenticated": "Meter Authenticated",
        "phone": "Tel No.",
        "address": "Address",
        "average_12m": "Average Last 12 Months",
        "status": "Meter Status",
        "zero_consumption": "Zero Consumption",
        "disc_consumption": "Disconnected and Consumption",
        "lat": "Y",  
        "lng": "X"   
    })
    
    columns_to_export = [
        "Contract Account", "Account Determination", "Meter Authenticated", 
        "Tel No.", "Address", "X", "Y", "Average Last 12 Months", 
        "Meter Status", "Zero Consumption", "Disconnected and Consumption"
    ]
    export_df = export_df[columns_to_export]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Filtered_Data')
    output.seek(0)
    
    return send_file(output, download_name="Marafiq_Export.xlsx", as_attachment=True)

# ══════════════════════════════════════════════════════
# تشغيل السيرفر
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌐 السيرفر جاهز! افتح الرابط في متصفحك:")
    print("👉 http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)
