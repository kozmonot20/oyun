import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math

class CasinoKuzenler:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuzenler Casino v1.0")
        self.root.geometry("650x720")
        self.root.configure(bg="#0b251a")

        # Ortak Kasa Sistemi (İki oyun da bu kasayı kullanır)
        self.kasa = 10000

        # Sekme Kontrolü (Tab Layout)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Sekme Stillerini Ayarla
        style = ttk.Style()
        style.configure("TNotebook", background="#0b251a")
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=5)

        # Sayfaları Oluştur
        self.tab_rulet = tk.Frame(self.notebook, bg="#0b251a")
        self.tab_slot = tk.Frame(self.notebook, bg="#1a0033")

        self.notebook.add(self.tab_rulet, text="  🎰 RULET MASASI  ")
        self.notebook.add(self.tab_slot, text="  🍒 SLOT MAKİNESİ  ")

        # Oyunları Başlat
        self.rulet_oyunu = RuletSekmesi(self.tab_rulet, self)
        self.slot_oyunu = SlotSekmesi(self.tab_slot, self)

    def kasa_guncelle(self, yeni_miktar, kaynak_secimi):
        self.kasa = yeni_miktar
        if self.kasa <= 0:
            messagebox.showwarning("Müflis", "Hesabınız sıfırlandı! Kumarhane size acıdı ve $10,000 kredi tanımladı.")
            self.kasa = 10000
        
        # İki sekmenin de bakiyesini anlık eşitle
        self.rulet_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")
        self.slot_oyunu.label_kasa.config(text=f"BAKİYE: ${self.kasa:,}")


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
        ust_panel = tk.Frame(self.frame, bg="#0b251a")
        ust_panel.pack(fill="x", padx=20, pady=10)

        self.label_kasa = tk.Label(ust_panel, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 18, "bold"), bg="#0b251a", fg="gold")
        self.label_kasa.pack(side="left")

        self.tabela_frame = tk.Frame(ust_panel, bg="#0b251a")
        self.tabela_frame.pack(side="right")
        tk.Label(self.tabela_frame, text="GEÇMİŞ:", font=("Arial", 10, "bold"), bg="#0b251a", fg="white").pack(side="left", padx=5)
        self.tabela_guncelle()

        self.canvas = tk.Canvas(self.frame, width=300, height=300, bg="#0b251a", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.cark_ve_top_ciz("Hazır", "gray", 0, None)
        bahis_frame = tk.LabelFrame(self.frame, text=" BAHİS ALANI ", font=("Arial", 11, "bold"), bg="#143626", fg="gold", bd=2)
        bahis_frame.pack(fill="x", padx=30, pady=10)

        tk.Label(bahis_frame, text="Bahis Türü:", font=("Arial", 10, "bold"), bg="#143626", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Radiobutton(bahis_frame, text="Sayıya Oyna (35 Katı)", variable=self.secilen_tur, value="Sayı", bg="#143626", fg="white", selectcolor="#0b251a", command=self.aktiflik_ayarla).grid(row=0, column=1, padx=5, sticky="w")
        tk.Radiobutton(bahis_frame, text="Renge Oyna (2 Katı)", variable=self.secilen_tur, value="Renk", bg="#143626", fg="white", selectcolor="#0b251a", command=self.aktiflik_ayarla).grid(row=0, column=2, padx=5, sticky="w")

        tk.Label(bahis_frame, text="Sayı Seç (0-36):", font=("Arial", 10, "bold"), bg="#143626", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_sayi = tk.Entry(bahis_frame, font=("Arial", 11, "bold"), width=6, justify="center")
        self.entry_sayi.grid(row=1, column=1, padx=5, sticky="w")
        self.entry_sayi.insert(0, "17")

        tk.Label(bahis_frame, text="Renk Seç:", font=("Arial", 10, "bold"), bg="#143626", fg="white").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.om_renk = tk.OptionMenu(bahis_frame, self.secilen_renk, "Kırmızı", "Siyah")
        self.om_renk.config(font=("Arial", 10), width=8, bg="#0b251a", fg="white", highlightthickness=0)
        self.om_renk.grid(row=1, column=3, padx=5, sticky="w")

        tk.Label(bahis_frame, text="Miktar ($):", font=("Arial", 10, "bold"), bg="#143626", fg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_miktar = tk.Entry(bahis_frame, font=("Arial", 11, "bold"), width=10, justify="center")
        self.entry_miktar.grid(row=2, column=1, padx=5, sticky="w")
        self.entry_miktar.insert(0, "500")

        self.label_durum = tk.Label(self.frame, text="Lütfen bahsinizi belirleyin ve çarkı çevirin.", font=("Arial", 12, "italic"), bg="#0b251a", fg="#a3b899")
        self.label_durum.pack(pady=10)

        self.btn_cevir = tk.Button(self.frame, text="🔥 ROULETTE WHEEL'I DÖNDÜR", font=("Helvetica", 14, "bold"), bg="#d4af37", fg="black", bd=4, command=self.bahis_isleme)
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
            bg_c = "#cc0000" if renk == "red" else ("#111111" if renk == "black" else "#00aa00")
            tk.Label(self.tabela_frame, text=f" {sayi} ", font=("Arial", 10, "bold"), bg=bg_c, fg="white", bd=1, relief="ridge").pack(side="left", padx=2)

    def cark_ve_top_ciz(self, merkez_metin, daire_renk, cark_acisi, top_acisi):
        self.canvas.delete("all")
        cx, cy, r = 150, 150, 120
        self.canvas.create_oval(cx-r-10, cy-r-10, cx+r+10, cy+r+10, fill="#2a1a08", outline="#d4af37", width=5)
        for i in range(12):
            dilim_aci = (i * 30) + cark_acisi
            x1 = cx + r * math.cos(math.radians(dilim_aci))
            y1 = cy + r * math.sin(math.radians(dilim_aci))
            self.canvas.create_line(cx, cy, x1, y1, fill="#554433", width=1)
        self.canvas.create_oval(cx-r+15, cy-r+15, cx+r-15, cy+r-15, fill=daire_renk, outline="white", width=2)
        self.canvas.create_oval(cx-45, cy-45, cx+45, cy+45, fill="#0b251a", outline="#d4af37", width=2)
        self.canvas.create_text(cx, cy, text=merkez_metin, fill="white", font=("Helvetica", 24, "bold"))
        if top_acisi is not None:
            tr = r - 25
            tx = cx + tr * math.cos(math.radians(top_acisi))
            ty = cy + tr * math.sin(math.radians(top_acisi))
            self.canvas.create_oval(tx-7, ty-7, tx+7, ty+7, fill="#fdfefe", outline="#bdc3c7", width=1)

    def bahis_isleme(self):
        try:
            miktar = int(self.entry_miktar.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz bahis miktarı!")
            return
        if miktar <= 0 or miktar > self.ana.kasa:
            messagebox.showerror("Hata", "Yetersiz bakiye veya geçersiz miktar!")
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
        
        self.ana.kasa_guncelle(self.ana.kasa - miktar, "rulet")
        self.btn_cevir.config(state="disabled")
        self.label_durum.config(text="Rien ne va plus! (Top dönüyor...)", fg="gold")
        self.animasyon_baslat(tür, hedef_sayi, miktar)

    def animasyon_baslat(self, tür, hedef_sayi, miktar):
        cark_acisi, top_acisi = 0, 0
        top_hizi, cark_hizi = 35.0, -5.0
        while top_hizi > 0.5:
            cark_acisi = (cark_acisi + cark_hizi) % 360
            top_acisi = (top_acisi + top_hizi) % 360
            gecici_sayi = random.randint(0, 36)
            self.cark_ve_top_ciz(str(gecici_sayi), self.renkler[gecici_sayi], cark_acisi, top_acisi)
            self.frame.update()
            top_hizi *= 0.94
            cark_hizi *= 0.95
            time.sleep(0.04)

        nihai_sayi = random.randint(0, 36)
        nihai_renk = self.renkler[nihai_sayi]
        self.cark_ve_top_ciz(str(nihai_sayi), nihai_renk, cark_acisi, top_acisi)
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
            self.ana.kasa_guncelle(self.ana.kasa + payout, "rulet")
            self.label_durum.config(text=f"🎉 KAZANDINIZ! Sonuç: {nihai_sayi} ({renk_isimi})", fg="#4ade80")
            messagebox.showinfo("Kazandınız!", f"Tebrikler! Masadan ${payout:,} çektiniz.")
        else:
            self.label_durum.config(text=f"Kaybettiniz. Sonuç: {nihai_sayi} ({renk_isimi})", fg="#f87171")
            self.ana.kasa_guncelle(self.ana.kasa, "rulet") 
        self.btn_cevir.config(state="normal")
class SlotSekmesi:
    def __init__(self, frame, ana_casino):
        self.frame = frame
        self.ana = ana_casino
        self.semboller = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣"]
        self.carpanlar = {"🍒": 5, "🍋": 8, "🍊": 12, "🍇": 15, "🔔": 25, "💎": 50, "7️⃣": 100}
        self.tasarla()

    def tasarla(self):
        self.label_kasa = tk.Label(self.frame, text=f"BAKİYE: ${self.ana.kasa:,}", font=("Helvetica", 20, "bold"), bg="#1a0033", fg="gold")
        self.label_kasa.pack(pady=20)

        # Matris Görünümü: Gerçekçi dikey akış için 3x3 Canvas yapısı
        self.canvas_slot = tk.Canvas(self.frame, width=380, height=200, bg="#0d001a", highlightthickness=3, highlightbackground="gold")
        self.canvas_slot.pack(pady=15)
        self.statik_matris_ciz(["7️⃣", "7️⃣", "7️⃣"])

        kontrol_frame = tk.Frame(self.frame, bg="#1a0033")
        kontrol_frame.pack(pady=15)

        tk.Label(kontrol_frame, text="Bahis Miktarı ($):", font=("Arial", 12, "bold"), bg="#1a0033", fg="white").grid(row=0, column=0, padx=10)
        self.entry_bahis = tk.Entry(kontrol_frame, font=("Arial", 12, "bold"), width=10, justify="center")
        self.entry_bahis.grid(row=0, column=1, padx=10)
        self.entry_bahis.insert(0, "100")

        self.label_durum = tk.Label(self.frame, text="Gerçekçi şerit akışını görmek için kolu çekin!", font=("Arial", 12, "italic"), bg="#1a0033", fg="#e0b0ff")
        self.label_durum.pack(pady=10)

        self.btn_spin = tk.Button(self.frame, text="🎰 SPIN / REELS'I DÖNDÜR", font=("Helvetica", 14, "bold"), bg="gold", fg="black", bd=5, command=self.bahis_kontrol)
        self.btn_spin.pack(pady=10)

    def statik_matris_ciz(self, merkez_semboller):
        self.canvas_slot.delete("all")
        for i in range(3):
            cx = 65 + (i * 125)
            self.canvas_slot.create_rectangle(cx-55, 65, cx+55, 135, fill="#1f003d", outline="#4d0099", width=2)
            self.canvas_slot.create_text(cx, 100, text=merkez_semboller[i], font=("Segoe UI Emoji", 48))
        self.canvas_slot.create_line(0, 100, 380, 100, fill="red", width=2, dash=(5, 3))

    def bahis_kontrol(self):
        try:
            bahis = int(self.entry_bahis.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz bahis miktarı!")
            return
        if bahis <= 0 or bahis > self.ana.kasa:
            messagebox.showerror("Hata", "Yetersiz bakiye veya geçersiz miktar!")
            return

        self.ana.kasa_guncelle(self.ana.kasa - bahis, "slot")
        self.btn_spin.config(state="disabled")
        self.label_durum.config(text="Makaralar akıyor...", fg="gold")
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
            time.sleep(0.04 + (s * 0.006))

        self.sonuc_isleme(nihai_sonuc, bahis)

    def sonuc_isleme(self, sonuclar, bahis):
        s1, s2, s3 = sonuclar
        if s1 == s2 == s3:
            kazanc = bahis * self.carpanlar[s1]
            self.ana.kasa_guncelle(self.ana.kasa + kazanc, "slot")
            self.label_durum.config(text=f"🎉 TEBRİKLER! 3'lü Kombinasyon! ${kazanc:,} kazandın!", fg="#4ade80")
            messagebox.showinfo("Tebrikler", f"Makaralar eşleşti! ${kazanc:,} kazandınız.")
        elif s1 == s2 or s2 == s3 or s1 == s3:
            self.ana.kasa_guncelle(self.ana.kasa + bahis, "slot")
            self.label_durum.config(text="Amorti! Çift yakaladın, paran iade.", fg="cyan")
        else:
            self.label_durum.config(text="Şansına küs! Eşleşme yok.", fg="#f87171")
            self.ana.kasa_guncelle(self.ana.kasa, "slot")
        self.btn_spin.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    uygulama = CasinoKuzenler(root)
    root.mainloop()
