import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math
import winsound  # Windows yerleşik ses motoru

class CasinoSesMotoru:
    """Oyun içi tüm 8-bit arcade tarzı ses efektlerini yöneten sınıf."""
    @staticmethod
    def tik_sesi():
        winsound.Beep(600, 30)

    @staticmethod
    def kazanc_sesi():
        winsound.Beep(523, 100) 
        winsound.Beep(659, 100) 
        winsound.Beep(784, 100) 
        winsound.Beep(1046, 250) 

    @staticmethod
    def kayip_sesi():
        winsound.Beep(392, 150) 
        winsound.Beep(349, 150) 
        winsound.Beep(311, 300) 

    @staticmethod
    def jackpot_sesi():
        for _ in range(3):
            winsound.Beep(880, 80)
            winsound.Beep(987, 80)
            winsound.Beep(1046, 120)

class CasinoKuzenlerBlack:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuzenler Casino v3.0 - Ultimate Edition")
        self.root.geometry("650x780")
        self.root.configure(bg="#050505")

        # Ortak Kasa
        self.kasa = 10000

        # Sekme Kontrolü (Tab Layout) ve Neon Teması
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
        self.tab_blackjack = tk.Frame(self.notebook, bg="#050505")

        self.notebook.add(self.tab_rulet, text="  🎰 NEON RULET  ")
        self.notebook.add(self.tab_slot, text="  🍒 MATRIX SLOT  ")
        self.notebook.add(self.tab_blackjack, text="  🃏 BLACKJACK (21)  ")

        # Sekme Sınıflarını Tetikleme
        self.rulet_oyunu = RuletSekmesi(self.tab_rulet, self)
        self.slot_oyunu = SlotSekmesi(self.tab_slot, self)
        self.blackjack_oyunu = BlackjackSekmesi(self.tab_blackjack, self)

    def bakiye_senkronize_et(self, yeni_miktar):
        self.kasa = yeni_miktar
        if self.kasa <= 0:
            CasinoSesMotoru.kayip_sesi()
            messagebox.showwarning("Müflis", "Paranız bitti! Kasa size $10,000 hibe etti.")
            self.kasa = 10000
        
        self.rulet_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")
        self.slot_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")
        self.blackjack_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")


class RuletSekmesi:
    def __init__(self, frame, ana_casino):
        self.frame = frame
        self.ana = ana_casino
        self.secilen_tur = tk.StringVar(value="Sayı")
        self.secilen_renk = tk.StringVar(value="Kırmızı")
        self.gecmis_sayilar = []

        self.renkler = {0: "green"}
        self.kirmizilar = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        for i in range(1, 37):
            self.renkler[i] = "red" if i in self.kirmizilar else "black"

        self.tasarla()

    def tasarla(self):
        ust_panel = tk.Frame(self.frame, bg="#050505")
        ust_panel.pack(fill="x", padx=20, pady=15)

        self.label_kasa = tk.Label(ust_panel, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 20, "bold"), bg="#050505", fg="#00ff66")
        self.label_kasa.pack(side="left")

        self.tabela_frame = tk.Frame(ust_panel, bg="#050505")
        self.tabela_frame.pack(side="right")
        tk.Label(self.tabela_frame, text="GEÇMİŞ:", font=("Arial", 10, "bold"), bg="#050505", fg="#888888").pack(side="left", padx=5)
        self.tabela_guncelle()

        self.canvas = tk.Canvas(self.frame, width=300, height=300, bg="#050505", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.cark_ve_top_ciz("Hazır", "#222222", 0, None)

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

        self.label_durum = tk.Label(self.frame, text="Neon masada bahisler açık.", font=("Arial", 11, "italic"), bg="#050505", fg="#888888")
        self.label_durum.pack(pady=10)

        self.btn_cevir = tk.Button(self.frame, text="⚡ CHIPS'LERİ SÜR VE DÖNDÜR", font=("Helvetica", 13, "bold"), bg="#00ff66", fg="#000000", activebackground="#00cc55", bd=0, cursor="hand2", command=self.bahis_isleme)
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
        ses_sayaci = 0
        
        while top_hizi > 0.6:
            cark_acisi = (cark_acisi + cark_hizi) % 360
            top_acisi = (top_acisi + top_hizi) % 360
            gecici_sayi = random.randint(0, 36)
            
            self.cark_ve_top_ciz(str(gecici_sayi), self.renkler[gecici_sayi], cark_acisi, top_acisi)
            self.frame.update()
            
            ses_sayaci += 1
            if ses_sayaci % 2 == 0:
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
            CasinoSesMotoru.kayip_sesi()
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

        self.btn_spin = tk.Button(self.frame, text="🚀 MATRIX STREAM'I BAŞLAT", font=("Helvetica", 13, "bold"), bg="gold", fg="black", activebackground="#cca300", bd=0, cursor="hand2", command=self.bahis_kontrol)
        self.btn_spin.pack(pady=10)

    def statik_matris_ciz(self, merkez_semboller):
        self.canvas_slot.delete("all")
        for i in range(3):
            cx = 65 + (i * 125)
            self.canvas_slot.create_rectangle(cx-55, 45, cx+55, 155, fill="#050505", outline="#222222", width=1)
            self.canvas_slot.create_text(cx, 100, text=merkez_semboller[i], font=("Segoe UI Emoji", 48, "bold"), fill="white")
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
            CasinoSesMotoru.kayip_sesi()
            self.label_durum.config(text="Eşleşme Sağlanamadı.", fg="#ff3333")
            self.ana.bakiye_senkronize_et(self.ana.kasa)
            
        self.btn_spin.config(state="normal", bg="gold")


class BlackjackSekmesi:
    def __init__(self, frame, ana_casino):
        self.frame = frame
        self.ana = ana_casino
        
        # Kart Serileri ve Skorları
        self.kart_tipleri = ['♠', '♥', '♦', '♣']
        self.kart_degerleri = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        self.deste = []
        self.oyuncu_eli = []
        self.kasa_eli = []
        self.aktif_bahis = 0
        self.oyun_devam_ediyor = False

        self.tasarla()

    def tasarla(self):
        self.label_kasa = tk.Label(self.frame, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 20, "bold"), bg="#050505", fg="#00ff66")
        self.label_kasa.pack(pady=15)

        # Kart Görselleştirme Alanı (Mat Siyah Alanlar)
        kartlar_frame = tk.Frame(self.frame, bg="#050505")
        kartlar_frame.pack(pady=10, fill="x", padx=40)

        # Kasa Bölümü
        kasa_pnl = tk.LabelFrame(kartlar_frame, text=" KRUPİYE (KASA) ", font=("Arial", 10, "bold"), bg="#111111", fg="#ff3333", bd=1, relief="solid")
        kasa_pnl.pack(fill="x", pady=5)
        self.lbl_kasa_skor = tk.Label(kasa_pnl, text="Skor: 0", bg="#111111", fg="white", font=("Arial", 10))
        self.lbl_kasa_skor.pack(anchor="w", padx=10)
        self.lbl_kasa_kartlar = tk.Label(kasa_pnl, text="[ - Boş - ]", bg="#111111", fg="gold", font=("Segoe UI Emoji", 20, "bold"), pady=10)
        self.lbl_kasa_kartlar.pack()

        # Oyuncu Bölümü
        oyuncu_pnl = tk.LabelFrame(kartlar_frame, text=" SİZ (OYUNCU) ", font=("Arial", 10, "bold"), bg="#111111", fg="#00ff66", bd=1, relief="solid")
        oyuncu_pnl.pack(fill="x", pady=10)
        self.lbl_oyuncu_skor = tk.Label(oyuncu_pnl, text="Skor: 0", bg="#111111", fg="white", font=("Arial", 10))
        self.lbl_oyuncu_skor.pack(anchor="w", padx=10)
        self.lbl_oyuncu_kartlar = tk.Label(oyuncu_pnl, text="[ - Boş - ]", bg="#111111", fg="gold", font=("Segoe UI Emoji", 20, "bold"), pady=10)
        self.lbl_oyuncu_kartlar.pack()

        # Alt Kontrol ve Bahis Çubuğu
        alt_frame = tk.Frame(self.frame, bg="#050505")
        alt_frame.pack(pady=10)

        tk.Label(alt_frame, text="Bahis ($):", font=("Arial", 11, "bold"), bg="#050505", fg="white").grid(row=0, column=0, padx=5)
        self.entry_bahis = tk.Entry(alt_frame, font=("Arial", 11, "bold"), width=10, justify="center", bg="#222222", fg="gold", bd=0, insertbackground="white")
        self.entry_bahis.grid(row=0, column=1, padx=5)
        self.entry_bahis.insert(0, "200")

        # Durum Göstergesi
        self.lbl_durum = tk.Label(self.frame, text="Bahis miktarını girip dağıtımı başlatın.", font=("Arial", 11, "italic"), bg="#050505", fg="#888888")
        self.lbl_durum.pack(pady=10)

        # Butonlar Kümesi
        btn_frame = tk.Frame(self.frame, bg="#050505")
        btn_frame.pack(pady=5)

        self.btn_dagit = tk.Button(btn_frame, text="🃏 KART DAĞIT", font=("Arial", 11, "bold"), bg="#00ff66", fg="black", bd=0, width=12, cursor="hand2", command=self.oyun_baslat)
        self.btn_dagit.grid(row=0, column=0, padx=5)

        self.btn_kart_cek = tk.Button(btn_frame, text="➕ KART ÇEK (HIT)", font=("Arial", 11, "bold"), bg="cyan", fg="black", bd=0, width=14, cursor="hand2", command=self.kart_cek)
        self.btn_kart_cek.grid(row=0, column=1, padx=5)

        self.btn_dur = tk.Button(btn_frame, text="✋ DUR (STAND)", font=("Arial", 11, "bold"), bg="orange", fg="black", bd=0, width=14, cursor="hand2", command=self.dur)
        self.btn_dur.grid(row=0, column=2, padx=5)

        self.buton_durumlarini_ayarla()

    def buton_durumlarini_ayarla(self):
        if self.oyun_devam_ediyor:
            self.btn_dagit.config(state="disabled", bg="#222222")
            self.btn_kart_cek.config(state="normal", bg="cyan")
            self.btn_dur.config(state="normal", bg="orange")
            self.entry_bahis.config(state="disabled")
        else:
            self.btn_dagit.config(state="normal", bg="#00ff66")
            self.btn_kart_cek.config(state="disabled", bg="#222222")
            self.btn_dur.config(state="disabled", bg="#222222")
            self.entry_bahis.config(state="normal")

    def deste_olustur(self):
        self.deste = []
        for tip in self.kart_tipleri:
            for isim in self.kart_degerleri.keys():
                self.deste.append((isim, tip))
        random.shuffle(self.deste)

    def el_skoru_hesapla(self, el):
        skor = 0
        as_sayisi = 0
        for isim, tip in el:
            skor += self.kart_degerleri[isim]
            if i_ad == 'A': # As kontrolü
                as_sayisi += 1
        # As'ları 11 yerine gerektiğinde 1 sayma esnekliği
        while skor > 21 and as_sayisi > 0:
            skor -= 10
            as_sayisi -= 1
        return skor

    def el_gorsel_metin(self, el, gizli=False):
        if not el: return "[ - Boş - ]"
        metinler = []
        for i, (isim, tip) in enumerate(el):
            if gizli and i == 1:
                metinler.append("🃏 [??]")
            else:
                metinler.append(f"{isim}{tip}")
        return "   ".join(metinler)

    def oyun_baslat(self):
        try:
            bahis = int(self.entry_bahis.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz bahis miktarı!")
            return
        if bahis <= 0 or bahis > self.ana.kasa:
            messagebox.showerror("Hata", "Yetersiz bakiye veya geçersiz miktar!")
            return

        self.aktif_bahis = bahis
        self.ana.bakiye_senkronize_et(self.ana.kasa - self.aktif_bahis)
        
        self.deste_olustur()
        self.oyuncu_eli = [self.deste.pop(), self.deste.pop()]
        self.kasa_eli = [self.deste.pop(), self.deste.pop()]
        
        self.oyun_devam_ediyor = True
        self.buton_durumlarini_ayarla()
        self.lbl_durum.config(text="Kartlar dağıtıldı. Kararınız?", fg="gold")

        # İlk ses efekti
        CasinoSesMotoru.tik_sesi()
        self.ekranlari_guncelle(kasa_gizli=True)

        # Doğal Blackjack Kontrolü
        if self.el_skoru_hesapla(self.oyuncu_eli) == 21:
            self.dur()

    def ekranlari_guncelle(self, kasa_gizli=True):
        o_skor = self.el_skoru_hesapla(self.oyuncu_eli)
        self.lbl_oyuncu_kartlar.config(text=self.el_gorsel_metin(self.oyuncu_eli))
        self.lbl_oyuncu_skor.config(text=f"Skor: {o_skor}")

        if kasa_gizli:
            self.lbl_kasa_kartlar.config(text=self.el_gorsel_metin(self.kasa_eli, gizli=True))
            # İlk kartın değerini göster
            ilk_kart_isim = self.kasa_eli[0][0]
            if ilk_kart_isim == 'A': ilk_skor = 11
            else: ilk_skor = self.kart_degerleri[ilk_kart_isim]
            self.lbl_kasa_skor.config(text=f"Skor: {ilk_skor} + ??")
        else:
            k_skor = self.el_skoru_hesapla(self.kasa_eli)
            self.lbl_kasa_kartlar.config(text=self.el_gorsel_metin(self.kasa_eli))
            self.lbl_kasa_skor.config(text=f"Skor: {k_skor}")

    def kart_cek(self):
        if not self.oyun_devam_ediyor: return
        
        CasinoSesMotoru.tik_sesi()
        self.oyuncu_eli.append(self.deste.pop())
        self.ekranlari_guncelle(kasa_gizli=True)

        if self.el_skoru_hesapla(self.oyuncu_eli) > 21:
            self.oyun_bitir("busted")

    def dur(self):
        if not self.oyun_devam_ediyor: return
        self.oyun_devam_ediyor = False
        
        # Kasanın Kart Çekme Safhası (Kasa 17'ye ulaşana kadar çeker)
        self.ekranlari_guncelle(kasa_gizli=False)
        while self.el_skoru_hesapla(self.kasa_eli) < 17:
            time.sleep(0.5)
            CasinoSesMotoru.tik_sesi()
            self.kasa_eli.append(self.deste.pop())
            self.ekranlari_guncelle(kasa_gizli=False)
            self.frame.update()

        o_skor = self.el_skoru_hesapla(self.oyuncu_eli)
        k_skor = self.el_skoru_hesapla(self.kasa_eli)

        if k_skor > 21:
            self.oyun_bitir("kasa_busted")
        elif o_skor > k_skor:
            self.oyun_bitir("oyuncu_kazandi")
        elif k_skor > o_skor:
            self.oyun_bitir("kasa_kazandi")
        else:
            self.oyun_bitir("beraberlik")

    def oyun_bitir(self, durum):
        self.oyun_devam_ediyor = False
        self.ekranlari_guncelle(kasa_gizli=False)
        
        if durum == "busted":
            CasinoSesMotoru.kayip_sesi()
            self.lbl_durum.config(text=f"Busted! 21'i geçtiniz. -${self.aktif_bahis:,}", fg="#ff3333")
            messagebox.showinfo("Sonuç", "21 Limitini geçerek kaybettiniz!")
            self.ana.bakiye_senkronize_et(self.ana.kasa)
        elif durum == "kasa_busted":
            CasinoSesMotoru.kazanc_sesi()
            kazanc = self.aktif_bahis * 2
            self.ana.bakiye_senkronize_et(self.ana.kasa + kazanc)
            self.lbl_durum.config(text=f"Kasa Busted! Kazandınız! +${self.aktif_bahis:,}", fg="#00ff66")
            messagebox.showinfo("Sonuç", "Kasa 21 limitini aştı, kazandınız!")
        elif durum == "oyuncu_kazandi":
            CasinoSesMotoru.kazanc_sesi()
            # Eğer tam doğal blackjack ise 2.5 katı verilir (1.5 katı ödül)
            if len(self.oyuncu_eli) == 2 and self.el_skoru_hesapla(self.oyuncu_eli) == 21:
                kazanc = int(self.aktif_bahis * 2.5)
                fark = kazanc - self.aktif_bahis
                self.lbl_durum.config(text=f"⚡ BLACKJACK! Müthiş Kazanç! +${fark:,}", fg="#00ff66")
            else:
                kazanc = self.aktif_bahis * 2
                self.lbl_durum.config(text=f"Tebrikler, Kazandınız! +${self.aktif_bahis:,}", fg="#00ff66")
                
            self.ana.bakiye_senkronize_et(self.ana.kasa + kazanc)
            messagebox.showinfo("Sonuç", "Daha yüksek skora ulaşarak eli aldınız!")
        elif durum == "kasa_kazandi":
            CasinoSesMotoru.kayip_sesi()
            self.lbl_durum.config(text=f"Kasa kazandı. -${self.aktif_bahis:,}", fg="#ff3333")
            messagebox.showinfo("Sonuç", "Kasa sizden daha yüksek bir skor yaptı!")
            self.ana.bakiye_senkronize_et(self.ana.kasa)
        elif durum == "beraberlik":
            # Parayı iade et
            self.ana.bakiye_senkronize_et(self.ana.kasa + self.aktif_bahis)
            self.lbl_durum.config(text="Beraberlik (Push)! Bahis miktarı iade.", fg="cyan")
            messagebox.showinfo("Sonuç", "Skorlar eşit, amorti!")

        self.buton_durumlarini_ayarla()


if __name__ == "__main__":
    root = tk.Tk()
    uygulama = CasinoKuzenlerBlack(root)
    root.mainloop()
