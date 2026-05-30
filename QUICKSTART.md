# 📚 StatusLC O'quv Markazi Boshqaruv Tizimi

## ✅ System Status: PRODUCTION READY

---

## 🎯 Nima Qilingan?

### 1️⃣ Professional Arxitektura Qurish (100%)
- ✅ 8 ta asosiy model
- ✅ 12 ta enum/status tizimi
- ✅ Audit trail (o'zgarish tarixini saqlash)
- ✅ Role-based access control
- ✅ Payment tracking system
- ✅ Attendance management
- ✅ Teacher salary calculation

### 2️⃣ Database Migratsiyalar (100%)
- ✅ Migration file yaratildi: `0004_discount_learningcenter_teachersalary_and_more.py`
- ✅ 35+ yangi maydon
- ✅ 7 ta performance index
- ✅ Database constraints

### 3️⃣ Admin Interface (100%)
- ✅ 8 ta professional admin class
- ✅ Color-coded status fields
- ✅ Inline editing
- ✅ Advanced filtering
- ✅ Bootstrap 5 templates

### 4️⃣ Documentation (100%)
- ✅ ARCHITECTURE.md - Batafsil arxitektura
- ✅ PROFESSIONAL_REBUILD.md - O'zgarishlar
- ✅ API_EXAMPLES.md - API misollari
- ✅ DEPLOYMENT.md - Deployment qo'llanma
- ✅ TESTING.md - Sinov qo'llanma

---

## 🚀 Boshlanish

### 1. Django Admin Paneliga Kirish

```
URL: http://localhost:8000/admin
Username: admin
Password: Status123LC@2026
```

### 2. Birinchi Qadamlar

**A. Learning Center Ma'lumotlari**
```
1. Admin paneliga kiring
2. Learning Centers → Add Learning Center
3. Markazing nomini, elektron pochtasi, manzilini kiriting
4. Standart to'lovni belgilang (masalan, 500,000 сўм)
```

**B. O'qituvchilarni Qo'shish**
```
1. Teachers → Add Teacher
2. To'liq ismi, email, telefon raqamini kiriting
3. Status: ACTIVE
4. Hire Date: Bugungi sana
5. Hourly Rate: Soat stavkasi (masalan, 50,000 сўм/soat)
```

**C. Guruhlarni Yaratish**
```
1. Groups → Add Group
2. Nomi, darajasi, jadval (kun/vaqt)
3. O'qituvchisini tayinlang
4. Maksimal o'quvchi soni (20-30 ta)
5. Oylik to'lovni belgilang (tuition_fee)
```

**D. O'quvchilarni Ro'yxatdan O'tkazish**
```
1. Students → Add Student
2. Shaxsiy ma'lumot (ismi, telefoni, tug'ilgan sanasi)
3. Ota-ona ma'lumoti
4. Guruhni tayinlang
5. Holati: ACTIVE
```

**E. To'lovlarni Qayd Etish**
```
1. Payments → Add Payment
2. O'quvchi va guruhni tanlang
3. O'ylni tanlang (Aprel = 2026-04-01)
4. To'lovni kiriting (500,000 сўм)
5. Status: PENDING yoki PAID
6. To'lov usuli: Cash/Card/Transfer
```

**F. Davomiylikni Yozish**
```
1. Attendances → Add Attendance
2. O'quvchi, guruh, dars sanasini tanlang
3. Status: PRESENT/ABSENT/LATE/EXCUSED
4. Dars davomiyligi (minut)
```

---

## 📊 Asosiy Modellar

### Teacher (O'qituvchi)
- ✅ Shaxsiy ma'lumot (ismi, email, telefon)
- ✅ Ishga olingan sana
- ✅ Soat stavkasi
- ✅ Status (Faol/Nofaol/Ta'tilda/Chiqarilgan)

### Group (Guruh)
- ✅ Jim va tasnifi
- ✅ Dars jadavli (kun + vaqt)
- ✅ O'qituvchi tayini
- ✅ Maksimal/minimal o'quvchi
- ✅ Oylik to'lov miqdori

### Student (O'quvchi)
- ✅ Shaxsiy ma'lumot
- ✅ Ota-ona ma'lumoti
- ✅ Ro'yxatlanish tarixin
- ✅ Ro'yxatlanish holati
- ✅ Guruh tayini

### Payment (To'lov)
- ✅ O'quvchi va to'landi guruh
- ✅ To'lov miqdori
- ✅ To'lov oyiga
- ✅ Status (To'langan/Kutilmoqda/Muddati o'tgan)
- ✅ To'lov usuli
- ✅ Chek raqami

### Attendance (Davomiylik)
- ✅ O'quvchi va guruh
- ✅ Dars sanasi
- ✅ Holati (Hozir/Yo'q/Kech/Oqlanuvchi)
- ✅ Dars davomiyligi

### Discount (Chegirma)
- ✅ Chegirma nomi va tafsiloti
- ✅ Foiz yoki soʻm
- ✅ Qaysi guruhlarga
- ✅ Qaysi o'quvchilarga
- ✅ Amal davri

### TeacherSalary (Maoshi)
- ✅ O'qituvchi va oy
- ✅ Dars soatlari
- ✅ Soat stavkasi
- ✅ Bonus va tahsil
- ✅ Jami maoshi
- ✅ To'lov holati

---

## 📱 API Endpointlari

### Authentication
```
POST /api/auth/login/
POST /api/auth/logout/
```

### Teachers (Admin only)
```
GET    /api/teachers/
POST   /api/teachers/
GET    /api/teachers/{id}/
PUT    /api/teachers/{id}/
DELETE /api/teachers/{id}/
```

### Groups
```
GET    /api/groups/
POST   /api/groups/
GET    /api/groups/{id}/
```

### Students
```
GET    /api/students/
POST   /api/students/
GET    /api/students/{id}/
GET    /api/students/unpaid/  - To'lanmagan
```

### Payments
```
GET    /api/payments/
POST   /api/payments/
GET    /api/payments/{id}/
```

### Attendance
```
GET    /api/attendances/
POST   /api/attendances/
GET    /api/attendances/{id}/
```

---

## 🔄 Kundalik Ishlar

### Har Hafta / Birinchi Kunida
```
1. Darsxonaga kelingan o'quvchilarning davomiylikni yozish
2. To'lanmagan to'lovlarni o'quvchilarga eslatma yuborish
```

### Har Oy Oxirida
```
1. Barcha to'lovlarni tasdiqlash
2. To'lanmagan to'lovlarni "OVERDUE" ga o'tkazish
3. O'qituvchi maoshini hisoblash
4. Oylik hisobot yaratish
```

### Har Chorak
```
1. O'quvchi davomiyligini tahlil qilish
2. Markazaning daromadin hisoblash
3. O'qituvchi ishlayotganlik baholash
```

---

## 🛠️ Admin Panel Haritasi

```
/admin/

📋 AUTHENTICATION & AUTHORIZATION
├── Users
├── Groups
└── Permissions

👥 ACCOUNTS (Foydalanuvchilar)
├── Profiles (Extended User Info)
└── User Management

🎓 CORE (O'quv Tizimi)
├── Learning Centers (Markazing Ma'lumoti)
├── Teachers (O'qituvchilar)
├── Groups (Guruhlar)
├── Students (O'quvchilar)
├── Payments (To'lovlar)
├── Discounts (Chegirmalar)
├── Attendances (Davomiylik)
└── Teacher Salaries (Maoshlar)

⚙️ JAZZMIN (UI)
├── Dashboard (Statistika)
├── Search (Qidirish)
└── Customization (Sozlamalar)
```

---

## 📈 Statistika va Hisobotlar

### Teacher Dashboard
- 👥 Jami o'quvchi
- 📚 Aktiv guruh
- 💰 Oylik to'lovlar

### Group Dashboard
- 👨‍🎓 Hozirgi o'quvchi
- 💵 Oy daromadi
- 📊 Davomiylik rate

### Student Dashboard
- 📚 Ro'yxatlanish holati
- 💰 To'dev holati
- 📈 Davomiylik foiz

---

## 💡 Foydalanish Misollari

### To'lanmagan O'quvchilarni Topish

```sql
SELECT student.first_name, student.last_name, 
       COUNT(*) as unpaid_months
FROM core_student student
LEFT JOIN core_payment payment 
  ON student.id = payment.student_id 
  AND payment.status = 'paid'
WHERE student.status = 'active'
AND payment.id IS NULL
GROUP BY student.id;
```

### Oylik Daromadin Hisoblash

```sql
SELECT 
  SUM(payment.amount) as monthly_income,
  COUNT(DISTINCT student.id) as paying_students
FROM core_payment payment
JOIN core_student student ON payment.student_id = student.id
WHERE MONTH(payment.month) = MONTH(CURDATE())
AND YEAR(payment.month) = YEAR(CURDATE());
```

### O'qituvchi Maoshi Hisoblash

```python
salary = TeacherSalary.objects.create(
    teacher=teacher,
    month=date(2026, 4, 1),
    teaching_hours=40,
    hourly_rate=50000,
    bonus=200000,
    deductions=150000
)
# Jami = (40 * 50000) + 200000 - 150000 = 2,050,000
```

---

## 🔐 Xavfsizlik Sozlamalari

✅ **Passwordlar Xashirovlangan**
- PBKDF2 algoritmi
- 260,000 iterations

✅ **CSRF Protection**
- Django CSRF middleware
- Token validation

✅ **SQL Injection Himoyasi**
- Django ORM parameterized queries

✅ **XSS Protection**
- Template autoescaping
- Safe HTML rendering

---

## 📞 Supp ort va Yordam

### Agar Jarayon Takliflari Yoki Xatolar Bo'lsa:

1. **Django Errors** - `/admin/` ishga tushish qiyinchiligi
2. **Model Errors** - Database migratsiya muammolari
3. **Permission Errors** - Foydalanuvchi roliga asoslangan masalalar

### Kontakt
- Email: support@statuslc.uz
- Phone: +998(99)123-4567

---

## 📚 Qo'shimcha Dokumentlarni O'qish

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Batafsil arxitektura
2. **[PROFESSIONAL_REBUILD.md](PROFESSIONAL_REBUILD.md)** - O'zgarishlar qo'llanmasi
3. **[API_EXAMPLES.md](API_EXAMPLES.md)** - API foydalanish
4. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Server sozlash
5. **[TESTING.md](TESTING.md)** - Sinov qo'llanmasi

---

## 🎉 Xulosa

**StatusLC o'quv markazi uchun to'lik professional boshqaruv tizimi:**

✅ Modern Django arxitekturasi  
✅ Professional Admin Panel  
✅ Complete Audit Trail  
✅ Status-based Management  
✅ Financial Tracking  
✅ Attendance System  
✅ Comprehensive Documentation  
✅ Production Ready  

**Dastur:** StatusLC v1.0 Professional  
**Holati:** 🟢 PRODUCTION READY  
**Oxirgi Yangilash:** 2026-04-19

---

**Boshqaruvni boshlashga tayinlangan!** 🚀

