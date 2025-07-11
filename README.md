# 📦 Cargo Privacy Web Application

## 📝 Proje Açıklaması
Bu proje, kargo teslimat süreçlerinde kişisel bilgilerin gizliliğini korumak amacıyla geliştirildi. Normalde alıcı adı, telefon numarası ve adres bilgileri kargo etiketlerine açıkça yazılır. Bu bilgiler birçok kişi tarafından görülebilir ve kötüye kullanılabilir.

Cargo Privacy Web Application, kişisel bilgilerin sadece yetkili kullanıcılar tarafından görülebilmesini sağlar. QR kod ve rol tabanlı erişim sistemi kullanılarak bilgilerin güvenliği sağlanır.


## 🚀 Özellikler
- 🔐 Rol bazlı erişim kontrolü
- 📱 QR kod ile güvenli bilgi paylaşımı
- ⏳ Otomatik oturum zaman aşımı
- 🔒 Şifrelenmiş kullanıcı verisi
- 🧾 UUID ile güvenli URL yapısı

## 👤 Kullanıcı Rolleri
- 🏢 **Şube Personeli**: Tüm kargo bilgilerine erişebilir
- 🚚 **Teslimat Görevlisi**: Sadece gerekli teslimat bilgilerine erişir

## 📸 QR Kod Kullanımı
- Şube personeli tarafından üretilen  QR kod pakete yapıştırılır.

- Teslimat görevlisi sisteme giriş yaptıktan sonra QR kodu tarar.

- Yetkisiz kişiler QR kodu tarasa bile bilgilere erişemez.


## ⚙️ Kurulum
```bash
git clone https://github.com/190101007/ship-scan.git
pip install -r requirements.txt
uvicorn main:app --reload

