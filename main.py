import flet as ft
import requests
import os

# --- AYARLAR ---
# PC'nin IP adresini buraya yaz (Sonunda / işareti olmasın)
BASE_URL = "http://192.168.1.100:5000"  

def main(page: ft.Page):
    page.title = "Transfer Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 700
    page.padding = 20

    # --- FONKSİYONLAR ---

    def giris_yap(e):
        sifre = sifre_input.value
        if not sifre:
            return
            
        try:
            page.snack_bar = ft.SnackBar(ft.Text("Bağlanılıyor..."))
            page.snack_bar.open = True
            page.update()
            
            # Sunucuya soruyoruz: Şifre doğru mu?
            r = requests.post(f"{BASE_URL}/api/login", json={"sifre": sifre}, timeout=3)
            
            if r.status_code == 200:
                page.clean() # Ekranı temizle
                panel_sayfasi() # Ana sayfaya geç
            else:
                hata_mesaji.value = "Hatalı Şifre!"
                hata_mesaji.update()
        except Exception as ex:
            hata_mesaji.value = f"Bağlantı Hatası: {ex}"
            hata_mesaji.update()

    def dosya_secildi(e: ft.FilePickerResultEvent):
        if e.files:
            secilen_dosya = e.files[0]
            # Dosyayı sunucuya gönder
            try:
                with open(secilen_dosya.path, "rb") as f:
                    files = {'file': (secilen_dosya.name, f)}
                    r = requests.post(f"{BASE_URL}/api/upload", files=files)
                    
                if r.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Dosya Gönderildi! ✅"))
                    panel_sayfasi() # Listeyi yenile
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Yükleme Başarısız ❌"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Hata: {ex}"))
            
            page.snack_bar.open = True
            page.update()

    def dosya_indir(dosya_ismi):
        # Tarayıcıda indirme linkini açar
        page.launch_url(f"{BASE_URL}/indir/{dosya_ismi}")

    # --- SAYFALAR ---

    def panel_sayfasi():
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        
        baslik = ft.Text("📂 Dosyalarım", size=25, weight="bold", color="blue")
        
        # Dosya Seçici (Görünmez yardımcı eleman)
        file_picker = ft.FilePicker(on_result=dosya_secildi)
        page.overlay.append(file_picker)

        yukle_btn = ft.ElevatedButton(
            "Dosya Yükle", 
            icon=ft.Icons.UPLOAD, # DÜZELTİLDİ
            bgcolor="blue", 
            color="white",
            on_click=lambda _: file_picker.pick_files(),
            width=300,
            height=45
        )
        
        yenile_btn = ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda _: panel_sayfasi()) # DÜZELTİLDİ

        dosya_listesi_kolon = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        # Sunucudan dosya listesini çek
        try:
            r = requests.get(f"{BASE_URL}/api/list", timeout=3)
            dosyalar = r.json().get("dosyalar", [])
            
            if not dosyalar:
                dosya_listesi_kolon.controls.append(ft.Text("Klasör boş...", italic=True))
            
            for d in dosyalar:
                kart = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color="white54"), # DÜZELTİLDİ
                            ft.Text(d, size=16, expand=True, no_wrap=True),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD, # DÜZELTİLDİ 
                                icon_color="green",
                                on_click=lambda e, x=d: dosya_indir(x)
                            )
                        ]),
                        padding=10
                    )
                )
                dosya_listesi_kolon.controls.append(kart)

        except:
            dosya_listesi_kolon.controls.append(ft.Text("Sunucuya ulaşılamadı!", color="red"))

        page.add(
            ft.Row([baslik, yenile_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(), 
            yukle_btn, 
            ft.Divider(), 
            dosya_listesi_kolon
        )
        page.update()


    # --- İLK AÇILIŞ (GİRİŞ EKRANI) ---
    sifre_input = ft.TextField(label="Giriş Şifresi", password=True, text_align="center", width=280)
    giris_btn = ft.ElevatedButton("Giriş Yap", on_click=giris_yap, width=280, height=50)
    hata_mesaji = ft.Text("", color="red")

    page.add(
        ft.Icon(ft.Icons.ROCKET_LAUNCH, size=80, color="blue"), # DÜZELTİLDİ
        ft.Text("Transfer Pro", size=20, weight="bold"),
        ft.Container(height=20),
        sifre_input,
        giris_btn,
        hata_mesaji
    )

ft.app(target=main)