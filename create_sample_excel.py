import pandas as pd
import random

columns = [
    "Contract Account", "Account Determination", "Meter Authenticated", 
    "Tel No.", "Address", "X", "Y", "Average Last 12 Months", 
    "Meter Status", "Zero Consumption", "Disconnected and Consumption"
]

# الإحداثيات الدقيقة بناءً على خريطة الجبيل الصناعية الفعلية
SECTOR_COORDS = {
    'A1': [27.085, 49.530], 'A2': [27.080, 49.540], 'A3': [27.075, 49.550], 'A4': [27.070, 49.535], 'A5': [27.090, 49.545], # جلمودة
    'B1': [27.050, 49.630], 'B2': [27.045, 49.640], 'B3': [27.040, 49.645], 'B4': [27.035, 49.635], 'B5': [27.030, 49.625], 'B6': [27.070, 49.635], # الفناتير
    'D1': [27.035, 49.570], 'D2': [27.030, 49.580], 'D3': [27.025, 49.590], 'D4': [27.020, 49.575], 'D5': [27.015, 49.585], # الدفي
    'F1': [26.985, 49.530], 'F2': [26.980, 49.540], 'F3': [26.975, 49.550], 'F4': [26.970, 49.535], # المطرفية
    'M':  [27.010, 49.630], 'N':  [26.995, 49.620], 'P':  [26.985, 49.635], 'Q':  [26.975, 49.645], 'R':  [27.000, 49.660], 'S':  [26.950, 49.620], 'T':  [27.005, 49.610]
}

zones = ["سكني", "تجاري", "حكومي", "صناعي"]
sectors_keys = list(SECTOR_COORDS.keys())
data = []

# توليد 160 سجل (40 لكل نوع)
for zone in zones:
    for _ in range(40):
        sec = random.choice(sectors_keys)
        base_lat = SECTOR_COORDS[sec][0]
        base_lng = SECTOR_COORDS[sec][1]
        
        # نثر البيوت حول مركز المحلة بمسافة عشوائية دقيقة (عشان تتوزع كأنها شوارع حقيقية)
        lat = round(base_lat + random.uniform(-0.006, 0.006), 5)
        lng = round(base_lng + random.uniform(-0.006, 0.006), 5)
        
        block = str(random.randint(10, 99))
        parcel = str(random.randint(1, 9)).zfill(2)
        bldg = str(random.randint(100, 999))
        address = f"{sec} {block} {parcel} {bldg}"

        is_active = random.choice([True, False])
        is_auth = random.choice(["موثق", "غير موثق"])
        
        meter_status = ""
        zero_cons = "لا"
        disc_cons = "لا"
        avg_cons = random.randint(100, 2000)

        if is_active:
            meter_status = "نشط" if is_auth == "موثق" else "نشط غير موثق"
            if random.random() < 0.15:
                zero_cons = "نعم"
                avg_cons = 0
        else:
            meter_status = "مفصول" if is_auth == "موثق" else "مفصول غير موثق"
            avg_cons = 0
            zero_cons = "نعم"
            if random.random() < 0.20:
                disc_cons = "نعم"
                zero_cons = "لا"
                meter_status = "مفصول ويوجد صرف"
                avg_cons = random.randint(50, 400)

        data.append({
            "Contract Account": f"100{random.randint(1000000, 9999999)}",
            "Account Determination": zone,
            "Meter Authenticated": is_auth,
            "Tel No.": f"05{random.randint(10000000, 99999999)}",
            "Address": address,
            "X": lng, 
            "Y": lat, 
            "Average Last 12 Months": avg_cons,
            "Meter Status": meter_status,
            "Zero Consumption": zero_cons,
            "Disconnected and Consumption": disc_cons
        })

df = pd.DataFrame(data)
df.to_excel("marafiq_real_data.xlsx", index=False)
print("✅ تم إنشاء الإكسل بناءً على الخريطة الحقيقية للجبيل!")
