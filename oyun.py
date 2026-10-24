import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math
import winsound  # Windows yerleşik ses motoru (Ekstra kütüphane gerektirmez)

class CasinoSesMotoru:
    """Oyun içi tüm 8-bit arcade tarzı ses efektlerini yöneten sınıf."""
    @staticmethod
    def tik_sesi():
        # Çark dönerken veya şerit akarken çalacak çıtlama sesi
        winsound.Beep(600, 30)

    @staticmethod
    def kazanc_sesi():
        # Başarılı kombinasyonlarda çalacak galibiyet melodisi
        winsound.Beep(523, 100) # C5
        winsound.Beep(659, 100) # E5
        winsound.Beep(784, 100) # G5
        winsound.Beep(1046, 250) # C6

    @staticmethod
    def kayıp_sesi():
        # Kaybedildiğinde çalacak dramatik düşüş sesi
        winsound.Beep(392, 150) # G4
        winsound.Beep(349, 150) # F4
        winsound.Beep(311, 300) # D#4

    @staticmethod
    def jackpot_sesi():
        # Büyük ikramiyede ortalığı yıkacak çılgın melodi
        for _ in range(3):
            winsound.Beep(880, 80)
            winsound.Beep(987, 80)
            winsound.Beep(1046, 120)

class CasinoKuzenlerBlack:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuzenler Casino v2.0 - Black Edition")
        self.root.geometry("650x750")
        self.root.configure(bg="#050505") # Tamamen siyah (Pitch Black) arka plan

        self.kasa = 10000

        # Sekme Kontrolü (Tab Layout) ve Black Edition Neon Teması
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#050505", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=10, background="#111111", foreground="#888888")
        style.map("TNotebook.Tab", background=[("selected", "#00ff66")], foreground=[("selected", "#000000")])

        # Sayfaları Tanımlama
        self.tab_rulet = tk.Frame(self.notebook, bg="#050505")
        self.tab_slot = tk.Frame(self.notebook, bg="#050505")

        self.notebook.add(self.tab_rulet, text="  🎰 NEON RULET  ")
        self.notebook.add(self.tab_slot, text="  🍒 MATRIX SLOT  ")

        # Sekme Sınıflarını Tetikleme
        self.rulet_oyunu = RuletSekmesi(self.tab_rulet, self)
        self.slot_oyunu = SlotSekmesi(self.tab_slot, self)

    def bakiye_senkronize_et(self, yeni_miktar):
        self.kasa = yeni_miktar
        if self.kasa <= 0:
            CasinoSesMotoru.kayıp_sesi()
            messagebox.showwarning("Müflis", "Paranız bitti! Kasa size $10,000 hibe etti.")
            self.kasa = 10000
        
        self.rulet_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")
        self.slot_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")
class RuletSekmesi:
    def __init__(self, frame, ana_casino):
        self.frame = frame
        self.ana = ana_casino
        self.secilen_tur = tk.StringVar(value="Sayı")
        self.secilen_renk = tk.StringVar(value="Kırmızı")
        self.gecmis_sayilar = []

        # Avrupa Ruleti Renk Kombinasyonları
        self.renkler = {0: "green"}
        self.kirmizilar = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        for i in range(1, 37):
            self.renkler[i] = "red" if i in self.kirmizilar else "black"

        self.tasarla()

    def tasarla(self):
        # Kasa Gösterge Paneli
        ust_panel = tk.Frame(self.frame, bg="#050505")
        ust_panel.pack(fill="x", padx=20, pady=15)

        self.label_kasa = tk.Label(ust_panel, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 20, "bold"), bg="#050505", fg="#00ff66")
        self.label_kasa.pack(side="left")

        self.tabela_frame = tk.Frame(ust_panel, bg="#050505")
        self.tabela_frame.pack(side="right")
        tk.Label(self.tabela_frame, text="GEÇMİŞ:", font=("Arial", 10, "bold"), bg="#050505", fg="#888888").pack(side="left", padx=5)
        self.tabela_guncelle()

        # Dijital Rulet Çark Tuvali
        self.canvas = tk.Canvas(self.frame, width=300, height=300, bg="#050505", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.cark_ve_top_ciz("Hazır", "#222222", 0, None)

        # Mat Black & Neon Bahis Alanı
        bahis_frame = tk.LabelFrame(self.frame, text=" BAHİS ODASI ", font=("Arial", 11, "bold"), bg="#111111", fg="#00ff66", bd=1, relief="solid")
        bahis_frame.pack(fill="x", padx=30, pady=15)

        tk.Label(bahis_frame, text="Bahis Türü:", font=("Arial", 10, "bold"), bg="#111111", fg="white").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        tk.Radiobutton(bahis_frame, text="Sayı (35x)", variable=self.secilen_tur, value="Sayı", bg="#111111", fg="white", selectcolor="#050505", activebackground="#111111", font=("Arial", 10), command=self.aktiflik_ayarla).grid(row=0, column=1, padx=5, sticky="w")
        tk.Radiobutton(bahis_frame, text="Renk (2x)", variable=self.secilen_tur, value="Renk", bg="#111111", fg="white", selectcolor="#050505", activebackground="#111111", font=("Arial", 10), command=self.aktiflik_ayarla).grid(row=0, column=2, padx=5, sticky="w")

        tk.Label(bahis_frame, text="Sayı (0-36):", font=("Arial", 10, "bold"), bg="#111111", fg="white").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_sayi = tk.Entry(bahis_frame, font=("Arial", 11, "bold"), width=6, justify="center", bg="#222222", fg="#00ff66", insertbackground="white", bd=0)
        self.entry_sayi.grid(row=1, column=1, padx=5, sticky="w")
        self.entry_sayi.insert(0, "17")

        tk.Label(bahis_frame, text="Renk:", font=("Arial", 10, "bold"), bg="#111111", fg="white").grid(row=1, column=2, padx=15, pady=10, sticky="w")
        self.om_renk = tk.OptionMenu(bahis_frame, self.secilen_renk, "Kırmızı", "Siyah")
        self.om_renk.config(font=("Arial", 10, "bold"), width=8, bg="#222222", fg="white", highlightthickness=0, bd=0)
        self.om_renk.grid(row=1, column=3, padx=5, sticky="w")
        tk.Label(bahis_frame, text="Miktar ($):", font=("Arial", 10, "bold"), bg="#111111", fg="white").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.entry_miktar = tk.Entry(bahis_frame, font=("Arial", 11, "bold"), width=12, justify="center", bg="#222222", fg="gold", insertbackground="white", bd=0)
        self.entry_miktar.grid(row=2, column=1, padx=5, sticky="w")
        self.entry_miktar.insert(0, "500")

        # Bilgi ve Tetikleyici Alanı
        self.label_durum = tk.Label(self.frame, text="Neon masada bahisler açık.", font=("Arial", 11, "italic"), bg="#050505", fg="#888888")
        self.label_durum.pack(pady=10)

        self.btn_cevir = tk.Button(self.frame, text="⚡ CHIPS'LERİ SÜR VE DÖNDÜR", font=("Helvetica", 13, "bold"), bg="#00ff66", fg="#000000", activebackground="#00cc55", bd=0, cursor="hand2", padding=8, command=self.bahis_isleme)
        self.btn_cevir.pack(pady=5)
        self.aktiflik_ayarla()

    def aktiflik_ayarla(self):
        if self.secilen_tur.get() == "Sayı":
            self.entry_sayi.config(state="normal")
            self.om_renk.config(state="disabled")
        else:
            self.entry_sayi.config(state="disabled")
            self.om_renk.config(state="normal")

    def tabela_guncelle(self):
        for widget in self.tabela_frame.winfo_children():
            if widget.winfo_class() == 'Label' and widget.cget("text") != "GEÇMİŞ:":
                widget.destroy()
        for sayi in self.gecmis_sayilar[-5:]:
            renk = self.renkler[sayi]
            bg_c = "#ff3333" if renk == "red" else ("#222222" if renk == "black" else "#00ff66")
            fg_c = "white" if renk != "green" else "black"
            tk.Label(self.tabela_frame, text=f" {sayi} ", font=("Arial", 10, "bold"), bg=bg_c, fg=fg_c, bd=1, relief="solid").pack(side="left", padx=2)

    def cark_ve_top_ciz(self, merkez_metin, daire_renk, cark_acisi, top_acisi):
        self.canvas.delete("all")
        cx, cy, r = 150, 150, 120
        # Siber Neon Halkalar
        self.canvas.create_oval(cx-r-10, cy-r-10, cx+r+10, cy+r+10, fill="#111111", outline="#00ff66", width=2)
        
        for i in range(12):
            dilim_aci = (i * 30) + cark_acisi
            x1 = cx + r * math.cos(math.radians(dilim_aci))
            y1 = cy + r * math.sin(math.radians(dilim_aci))
            self.canvas.create_line(cx, cy, x1, y1, fill="#222222", width=1)
            
        self.canvas.create_oval(cx-r+15, cy-r+15, cx+r-15, cy+r-15, fill=daire_renk, outline="#050505", width=2)
        self.canvas.create_oval(cx-45, cy-45, cx+45, cy+45, fill="#050505", outline="#00ff66", width=1)
        
        gorsel_renk = "#00ff66" if daire_renk == "green" else ("#ff3333" if daire_renk == "red" else "white")
        if merkez_metin == "Hazır": gorsel_renk = "white"
        
        self.canvas.create_text(cx, cy, text=merkez_metin, fill=gorsel_renk, font=("Helvetica", 24, "bold"))
        
        if top_acisi is not None:
            tr = r - 22
            tx = cx + tr * math.cos(math.radians(top_acisi))
            ty = cy + tr * math.sin(math.radians(top_acisi))
            self.canvas.create_oval(tx-8, ty-8, tx+8, ty+8, fill="#ffffff", outline="#00ff66", width=2)
    def bahis_isleme(self):
        try:
            miktar = int(self.entry_miktar.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz bahis miktarı!")
            return
        if miktar <= 0 or miktar > self.ana.kasa:
            messagebox.showerror("Hata", "Yetersiz bakiye!")
            return
        tür = self.secilen_tur.get()
        hedef_sayi = None
        if tür == "Sayı":
            try:
                hedef_sayi = int(self.entry_sayi.get())
                if hedef_sayi < 0 or hedef_sayi > 36: raise ValueError
            except ValueError:
                messagebox.showerror("Hata", "Sayı 0 ile 36 arasında olmalıdır!")
                return
        
        self.ana.bakiye_senkronize_et(self.ana.kasa - miktar)
        self.btn_cevir.config(state="disabled", bg="#222222")
        self.label_durum.config(text="Rien ne va plus! Top siber yörüngede...", fg="gold")
        self.animasyon_baslat(tür, hedef_sayi, miktar)

    def animasyon_baslat(self, tür, hedef_sayi, miktar):
        cark_acisi, top_acisi = 0, 0
        top_hizi, cark_hizi = 38.0, -4.0
        ses_sayacı = 0
        
        while top_hizi > 0.6:
            cark_acisi = (cark_acisi + cark_hizi) % 360
            top_acisi = (top_acisi + top_hizi) % 360
            gecici_sayi = random.randint(0, 36)
            
            self.cark_ve_top_ciz(str(gecici_sayi), self.renkler[gecici_sayi], cark_acisi, top_acisi)
            self.frame.update()
            
            # Her 2 döngüde bir mekanik çıtlama sesi tetikle
            ses_sayacı += 1
            if ses_sayacı % 2 == 0:
                CasinoSesMotoru.tik_sesi()
                
            top_hizi *= 0.94
            cark_hizi *= 0.96
            time.sleep(0.04)

        nihai_sayi = random.randint(0, 36)
        nihai_renk = self.renkler[nihai_sayi]
        self.cark_ve_top_ciz(str(nihai_sayi), nihai_renk, cark_acisi, top_acisi + 0.5)
        self.gecmis_sayilar.append(nihai_sayi)
        self.tabela_guncelle()

        kazandi = False
        payout = 0
        renk_isimi = "KIRMIZI" if nihai_renk == "red" else ("SİYAH" if nihai_renk == "black" else "YEŞİL")
        
        if tür == "Sayı" and hedef_sayi == nihai_sayi:
            kazandi = True
            payout = miktar * 36
        elif tür == "Renk":
            tahmin_renk_eng = "red" if self.secilen_renk.get() == "Kırmızı" else "black"
            if tahmin_renk_eng == nihai_renk:
                kazandi = True
                payout = miktar * 2

        if kazandi:
            CasinoSesMotoru.kazanc_sesi()
            self.ana.bakiye_senkronize_et(self.ana.kasa + payout)
            self.label_durum.config(text=f"🎉 TEBRİKLER! {nihai_sayi} ({renk_isimi}) Kazandı!", fg="#00ff66")
            messagebox.showinfo("Kuzenler Matrix", f"Kasa Patladı! ${payout:,} kazandınız.")
        else:
            CasinoSesMotoru.kayıp_sesi()
            self.label_durum.config(text=f"Kasa Aldı! Sonuç: {nihai_sayi} ({renk_isimi})", fg="#ff3333")
            self.ana.bakiye_senkronize_et(self.ana.kasa)
            
        self.btn_cevir.config(state="normal", bg="#00ff66")
class SlotSekmesi:
    def __init__(self, frame, ana_casino):
        self.frame = frame
        self.ana = ana_casino
        self.semboller = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣"]
        self.carpanlar = {"🍒": 5, "🍋": 8, "🍊": 12, "🍇": 15, "🔔": 25, "💎": 50, "7️⃣": 100}
        self.tasarla()

    def tasarla(self):
        self.label_kasa = tk.Label(self.frame, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 20, "bold"), bg="#050505", fg="#00ff66")
        self.label_kasa.pack(pady=20)

        # Siber Grid: Neon Yeşil Hatlara Sahip Dijital Matris Paneli
        self.canvas_slot = tk.Canvas(self.frame, width=380, height=200, bg="#111111", highlightthickness=2, highlightbackground="#00ff66")
        self.canvas_slot.pack(pady=15)
        self.statik_matris_ciz(["7️⃣", "7️⃣", "7️⃣"])

        kontrol_frame = tk.Frame(self.frame, bg="#050505")
        kontrol_frame.pack(pady=15)

        tk.Label(kontrol_frame, text="Miktar ($):", font=("Arial", 12, "bold"), bg="#050505", fg="white").grid(row=0, column=0, padx=10)
        self.entry_bahis = tk.Entry(kontrol_frame, font=("Arial", 12, "bold"), width=12, justify="center", bg="#222222", fg="gold", bd=0, insertbackground="white")
        self.entry_bahis.grid(row=0, column=1, padx=10)
        self.entry_bahis.insert(0, "100")

        self.label_durum = tk.Label(self.frame, text="Makaraları Matrix akışına bırakın.", font=("Arial", 11, "italic"), bg="#050505", fg="#888888")
        self.label_durum.pack(pady=10)

        self.btn_spin = tk.Button(self.frame, text="🚀 MATRIX STREAM'I BAŞLAT", font=("Helvetica", 13, "bold"), bg="gold", fg="black", activebackground="#cca300", bd=0, cursor="hand2", padding=8, command=self.bahis_kontrol)
        self.btn_spin.pack(pady=10)

    def statik_matris_ciz(self, merkez_semboller):
        self.canvas_slot.delete("all")
        for i in range(3):
            cx = 65 + (i * 125)
            # Dijital Makaraların Arka Yuvaları
            self.canvas_slot.create_rectangle(cx-55, 45, cx+55, 155, fill="#050505", outline="#222222", width=1)
            self.canvas_slot.create_text(cx, 100, text=merkez_semboller[i], font=("Segoe UI Emoji", 48))
        # Siber Hedef Çizgisi (Laser Payline)
        self.canvas_slot.create_line(0, 100, 380, 100, fill="#ff3333", width=2, dash=(6, 4))
    def bahis_kontrol(self):
        try:
            bahis = int(self.entry_bahis.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz bahis miktarı!")
            return
        if bahis <= 0 or bahis > self.ana.kasa:
            messagebox.showerror("Hata", "Yetersiz bakiye!")
            return

        self.ana.bakiye_senkronize_et(self.ana.kasa - bahis)
        self.btn_spin.config(state="disabled", bg="#222222")
        self.label_durum.config(text="Şerit akışı optimize ediliyor...", fg="gold")
        self.slot_akisi_baslat(bahis)

    def slot_akisi_baslat(self, bahis):
        nihai_sonuc = [random.choice(self.semboller) for _ in range(3)]
        adımlar = 25
        
        for s in range(adımlar):
            anlik_ekran = []
            for col in range(3):
                if s < 12 and col == 0: anlik_ekran.append(random.choice(self.semboller))
                elif col == 0: anlik_ekran.append(nihai_sonuc[0])
                
                if s < 18 and col == 1: anlik_ekran.append(random.choice(self.semboller))
                elif col == 1: anlik_ekran.append(nihai_sonuc[1])
                
                if s < 25 and col == 2: anlik_ekran.append(random.choice(self.semboller))
                elif col == 2: anlik_ekran.append(nihai_sonuc[2])

            self.statik_matris_ciz(anlik_ekran)
            self.frame.update()
            
            # Her şerit kaymasında dijital çıtlama sesi tetikle
            CasinoSesMotoru.tik_sesi()
            time.sleep(0.04 + (s * 0.005))

        self.sonuc_isleme(nihai_sonuc, bahis)

    def sonuc_isleme(self, sonuclar, bahis):
        s1, s2, s3 = sonuclar
        if s1 == s2 == s3:
            kazanc = bahis * self.carpanlar[s1]
            self.ana.bakiye_senkronize_et(self.ana.kasa + kazanc)
            
            if s1 == "7️⃣":
                CasinoSesMotoru.jackpot_sesi()
                self.label_durum.config(text=f"🚨 MATRIX JACKPOT VURULDU! +${kazanc:,}", fg="#00ff66")
                messagebox.showinfo("JACKPOT", f"Sistem Kilitlendi! 777 Kombinasyonu: ${kazanc:,}")
            else:
                CasinoSesMotoru.kazanc_sesi()
                self.label_durum.config(text=f"🎉 Matrix Eşleşmesi Başarılı! +${kazanc:,}", fg="#00ff66")
                messagebox.showinfo("Tebrikler", f"Makaralar eşleşti: ${kazanc:,}")
                
        elif s1 == s2 or s2 == s3 or s1 == s3:
            CasinoSesMotoru.kazanc_sesi()
            self.ana.bakiye_senkronize_et(self.ana.kasa + bahis)
            self.label_durum.config(text="Amorti Sinyali! Bahis iade edildi.", fg="cyan")
        else:
            CasinoSesMotoru.kayıp_sesi()
            self.label_durum.config(text="Eşleşme Sağlanamadı.", fg="#ff3333")
            self.ana.bakiye_senkronize_et(self.ana.kasa)
            
        self.btn_spin.config(state="normal", bg="gold")

# Uygulama Başlatıcı Ana Döngü
if __name__ == "__main__":
    root = tk.Tk()
    uygulama = CasinoKuzenlerBlack(root)
    root.mainloop()
