# 🍫 مستندات مدیر پروژه Chocolate

Chocolate یک مدیر پروژه سبک است که برای مدیریت محیط‌های مجازی، کنترل وابستگی‌ها و خودکارسازی وظایف پروژه طراحی شده است.

## 🎯 **استفاده**



```bash
chocolate <command> [گزینه‌ها] [آرگومان‌ها]
```

## 📂 **ایجاد یک پروژه جدید**



```bash
chocolate new <project name> <main file name>
```

## 🚀 **اجرا کردن پروژه**



```bash
chocolate run
```

- فایل اصلی پروژه را درون محیط مجازی اجرا می‌کند.
- به‌طور خودکار متغیرهای محیطی و پرچم‌ها را بارگذاری می‌کند.

### ✅ مثال:



```bash
chocolate run
```

### با پرچم `--reinstall` (اجبار به نصب مجدد وابستگی‌ها):



```bash
chocolate run --reinstall
```

## **💻 یکسان سازی با سرور**

```bash
chocolate sync
```

### تغییر مشخصات سرور:

```bash
chocolate ssh <Hostname> <SSHPort> <SSHUsername> <SSHPassword>
```


## 📦 **مدیریت بسته‌ها**

### نصب بسته‌ها:



```bash
chocolate add <dependency> ...
```

- بسته‌ها را نصب و به پیکربندی `.chocolate` اضافه می‌کند.

### ✅ مثال:



```bash
chocolate add rich requests flask
```

### نصب مجدد تمام بسته‌ها:



```bash
chocolate reinstall
```

## 🌐 **مدیریت متغیرهای محیطی**

### فهرست تمام متغیرها:



```bash
chocolate env list
```

### اضافه کردن متغیرهای محیطی:



```
chocolate env VAR1=value VAR2=value
```

### حذف متغیرها:



```bash
chocolate env remove VAR1 VAR2
```

### خصوصی/عمومی کردن متغیر:
متغیر های خصوصی با دستور اکسپورت استخراج نمیشوند.


```bash
chocolate env private VAR1 VAR2
```

## 🏁 **مدیریت پرچم‌ها**



```bash
chocolate flags <flags>
```

### ✅ مثال:



```bash
chocolate flags --debug --fast
```

## 🛠️ **عملیات سفارشی**

### اضافه کردن یک عملیات جدید:


```bash
chocolate action add <name> <code>
```

- Use `-i <filename>` to insert multiple line bash.

### حذف یک عملیات:



```bash
chocolate action remove <نام_عملیات>
```

### اجرای یک عملیات:



```bash
chocolate action <نام_عملیات>
```

## 🛤️ **مدیریت مسیرها**

### استثنا کردن مسیرها:



```bash
chocolate path exclude <مسیر1> <مسیر2>
```

### شامل کردن مجدد مسیرها:



```bash
chocolate path include <مسیر1> <مسیر2>
```

### فهرست مسیرهای استثنا شده:



```bash
chocolate path list
```

## 📤 **اکسپورت پروژه**

bash

```
chocolate export -o <output.zip>
```

## 📝 **کمک**



```bash
chocolate help
```


## مشاهده فایل کانفیگ
```bash
chocolate config
```

## استفاده از sandbox
با استفاده از سندباکس میتونید مموری/سی پی یو تایم/سی پی یو فریکوئنسی اپ اتون رو محدود کنید.
این کامند رو برای اطلاعات بیشتر بزنید.
‍‍```bash
chocolate sandbox 
```

## 🔥 **مثال‌ها**



```bash
# ایجاد یک پروژه
chocolate new -n my_project -m main.py

# نصب بسته‌ها
chocolate add requests rich flask

# اجرای پروژه
chocolate run

# اضافه کردن متغیر محیطی
chocolate env API_KEY=123456789

# نصب مجدد تمام بسته‌ها
chocolate reinstall

# صادرات پروژه به صورت zip
chocolate export -o my_project.zip
```



## ✅ **نتیجه‌گیری**

مدیر پروژه Chocolate برای مدیریت تمام مراحل از راه‌اندازی پروژه تا مدیریت وابستگی‌ها و خودکارسازی سفارشی طراحی شده است.