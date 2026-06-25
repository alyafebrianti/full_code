import cv2
import numpy as np
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# ============================================================
#  Aplikasi Pengolahan Citra - UAS
#  Fitur: Upload hingga 20 gambar, proses 6 tahapan,
#          hasil digabung menjadi satu grid output
#  UI: CustomTkinter (Modern Dark Theme)
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---- Ukuran cell gambar ----
CELL_W = 140
CELL_H = 105

# ---- Warna Kustom ----
C = {
    "bg":           "#0f0f1a",
    "card":         "#1a1a2e",
    "card_light":   "#222240",
    "sidebar":      "#12122a",
    "accent":       "#6c63ff",
    "accent_h":     "#8b83ff",
    "success":      "#00c896",
    "success_h":    "#00e6ac",
    "danger":       "#ff4757",
    "danger_h":     "#ff6b7a",
    "warn":         "#ffa502",
    "text":         "#e4e4f0",
    "text_dim":     "#7a7a9e",
    "text_bright":  "#ffffff",
    "border":       "#2e2e50",
    "cell_border":  "#3a3a5c",
    "header_bg":    "#6c63ff",
    "col_label":    "#2a2a4a",
    "row_even":     "#16162e",
    "row_odd":      "#1e1e3a",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Pengolahan Citra - UAS")
        self.geometry("1400x870")
        self.minsize(1200, 700)
        self.configure(fg_color=C["bg"])

        # Data
        self.image_paths = []
        self.cv_images = []
        self.thumb_refs = []
        self._img_refs = []
        self.max_images = 20

        # Layout
        self._build_ui()

    # ================================================================
    #  BUILD UI
    # ================================================================
    def _build_ui(self):
        # ---- Top accent stripe ----
        stripe = ctk.CTkFrame(self, fg_color=C["accent"], height=3, corner_radius=0)
        stripe.pack(fill="x", side="top")

        # ---- Header ----
        header = ctk.CTkFrame(self, fg_color=C["card"], height=60, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="PENGOLAHAN CITRA",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=C["text_bright"],
        ).pack(side="left", padx=28, pady=12)

        ctk.CTkLabel(
            header, text="UAS  |  Upload 20 Gambar  |  6 Tahapan  |  Hasil Gabungan",
            font=ctk.CTkFont(size=12),
            text_color=C["text_dim"],
        ).pack(side="left", padx=6)

        # ---- Main body ----
        body = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_content(body)

        # ---- Status bar ----
        sbar = ctk.CTkFrame(self, fg_color=C["card"], height=28, corner_radius=0)
        sbar.pack(fill="x", side="bottom")
        sbar.pack_propagate(False)
        self.lbl_status = ctk.CTkLabel(
            sbar, text="Siap digunakan",
            font=ctk.CTkFont(size=11), text_color=C["text_dim"], anchor="w",
        )
        self.lbl_status.pack(fill="x", padx=20, pady=3)

    # ---- SIDEBAR ----
    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=C["sidebar"], width=310, corner_radius=0)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        px = 18

        # ---- Judul sidebar ----
        ctk.CTkLabel(
            sidebar, text="KONTROL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["text_dim"],
        ).pack(anchor="w", padx=px, pady=(20, 12))

        # ---- Tombol Upload ----
        ctk.CTkButton(
            sidebar, text="Upload Gambar",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=C["accent"], hover_color=C["accent_h"],
            text_color=C["text_bright"],
            height=44, corner_radius=10,
            command=self.load_images,
        ).pack(fill="x", padx=px, pady=(0, 8))

        # ---- Tombol Proses ----
        ctk.CTkButton(
            sidebar, text="Proses Semua",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=C["success"], hover_color=C["success_h"],
            text_color=C["text_bright"],
            height=44, corner_radius=10,
            command=self.process_all,
        ).pack(fill="x", padx=px, pady=(0, 8))

        # ---- Tombol Hapus ----
        ctk.CTkButton(
            sidebar, text="Hapus Semua",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=C["danger"], hover_color=C["danger_h"],
            text_color=C["text_bright"],
            height=44, corner_radius=10,
            command=self.clear_all,
        ).pack(fill="x", padx=px, pady=(0, 4))

        # ---- Separator ----
        ctk.CTkFrame(sidebar, fg_color=C["border"], height=1, corner_radius=0).pack(
            fill="x", padx=px, pady=16
        )

        # ---- Counter ----
        self.lbl_count = ctk.CTkLabel(
            sidebar, text="Gambar: 0 / 20",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["text"],
        )
        self.lbl_count.pack(anchor="w", padx=px)

        # ---- Progress bar ----
        self.progress = ctk.CTkProgressBar(
            sidebar, progress_color=C["accent"],
            fg_color=C["border"], height=8, corner_radius=4,
        )
        self.progress.pack(fill="x", padx=px, pady=(8, 4))
        self.progress.set(0)

        self.lbl_progress = ctk.CTkLabel(
            sidebar, text="Siap memproses",
            font=ctk.CTkFont(size=11), text_color=C["text_dim"],
        )
        self.lbl_progress.pack(anchor="w", padx=px)

        # ---- Separator ----
        ctk.CTkFrame(sidebar, fg_color=C["border"], height=1, corner_radius=0).pack(
            fill="x", padx=px, pady=16
        )

        # ---- Daftar gambar label ----
        ctk.CTkLabel(
            sidebar, text="DAFTAR GAMBAR",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["text_dim"],
        ).pack(anchor="w", padx=px, pady=(0, 8))

        # ---- Scrollable frame untuk daftar ----
        self.img_list_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color=C["sidebar"],
            scrollbar_button_color=C["border"],
            scrollbar_button_hover_color=C["accent"],
            corner_radius=0,
        )
        self.img_list_frame.pack(fill="both", expand=True, padx=(px, 4), pady=(0, 10))

    # ---- CONTENT AREA ----
    def _build_content(self, parent):
        content = ctk.CTkFrame(parent, fg_color=C["bg"], corner_radius=0)
        content.pack(fill="both", expand=True, side="left")

        # Title
        top = ctk.CTkFrame(content, fg_color=C["bg"], corner_radius=0)
        top.pack(fill="x", padx=24, pady=(16, 8))

        self.lbl_title = ctk.CTkLabel(
            top, text="Hasil Pengolahan Citra",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C["text_bright"],
        )
        self.lbl_title.pack(side="left")

        # ---- Preview card ----
        self.preview_card = ctk.CTkFrame(content, fg_color=C["card"], corner_radius=14)
        self.preview_card.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Scrollable area di dalam card
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.preview_card, fg_color=C["card"],
            scrollbar_button_color=C["border"],
            scrollbar_button_hover_color=C["accent"],
            corner_radius=12,
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self._show_placeholder()

    def _show_placeholder(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self._img_refs.clear()

        # Placeholder card
        ph = ctk.CTkFrame(self.scroll_frame, fg_color=C["card_light"], corner_radius=16)
        ph.pack(expand=True, pady=120, padx=40)

        ctk.CTkLabel(
            ph, text="Upload gambar lalu klik  Proses Semua",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C["text_dim"],
        ).pack(padx=60, pady=(40, 4))

        ctk.CTkLabel(
            ph, text="Hasil pengolahan 6 tahapan akan ditampilkan di sini",
            font=ctk.CTkFont(size=12),
            text_color=C["text_dim"],
        ).pack(padx=60, pady=(0, 40))

    # ================================================================
    #  LOAD IMAGES
    # ================================================================
    def load_images(self):
        paths = filedialog.askopenfilenames(
            title="Pilih Gambar (Maks. 20)",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All Files", "*.*")],
        )
        if not paths:
            return

        remaining = self.max_images - len(self.image_paths)
        if remaining <= 0:
            messagebox.showwarning("Batas Tercapai", f"Sudah mencapai {self.max_images} gambar.")
            return
        if len(paths) > remaining:
            messagebox.showinfo("Info", f"Hanya {remaining} slot tersisa.")
            paths = paths[:remaining]

        ok = 0
        for p in paths:
            img = cv2.imread(p)
            if img is not None:
                self.image_paths.append(p)
                self.cv_images.append(img)
                ok += 1

        self._refresh_list()
        self._update_count()
        self.lbl_status.configure(text=f"{ok} gambar dimuat  |  Total: {len(self.image_paths)}")
        self.progress.set(0)
        self.lbl_progress.configure(text="Siap memproses")

    # ================================================================
    #  SIDEBAR IMAGE LIST
    # ================================================================
    def _refresh_list(self):
        for w in self.img_list_frame.winfo_children():
            w.destroy()
        self.thumb_refs.clear()

        for idx, (path, img) in enumerate(zip(self.image_paths, self.cv_images)):
            # Card per item
            card = ctk.CTkFrame(self.img_list_frame, fg_color=C["card"], corner_radius=10, height=60)
            card.pack(fill="x", pady=3)
            card.pack_propagate(False)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=8, pady=6)
            inner.columnconfigure(1, weight=1)

            # Thumbnail
            thumb = self._cv_to_ctk(img, (44, 44))
            self.thumb_refs.append(thumb)
            ctk.CTkLabel(inner, image=thumb, text="").grid(row=0, column=0, rowspan=2, padx=(0, 10))

            # Nama file
            name = os.path.basename(path)
            if len(name) > 22:
                name = name[:19] + "..."
            ctk.CTkLabel(
                inner, text=f"{idx + 1}. {name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=C["text"], anchor="w",
            ).grid(row=0, column=1, sticky="w")

            # Dimensi
            h, w = img.shape[:2]
            ctk.CTkLabel(
                inner, text=f"{w} x {h} px",
                font=ctk.CTkFont(size=10),
                text_color=C["text_dim"], anchor="w",
            ).grid(row=1, column=1, sticky="w")

            # Tombol hapus
            ctk.CTkButton(
                inner, text="x", width=28, height=28,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=C["card_light"], hover_color=C["danger"],
                text_color=C["danger"], corner_radius=6,
                command=lambda i=idx: self._remove(i),
            ).grid(row=0, column=2, rowspan=2, padx=(6, 0))

    def _cv_to_ctk(self, cv_img, size):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil.thumbnail(size, Image.LANCZOS)
        return ctk.CTkImage(pil, size=size)

    def _remove(self, idx):
        if 0 <= idx < len(self.image_paths):
            del self.image_paths[idx]
            del self.cv_images[idx]
            self._refresh_list()
            self._update_count()
            self.lbl_status.configure(text=f"Gambar dihapus  |  Total: {len(self.image_paths)}")

    def _update_count(self):
        n = len(self.image_paths)
        self.lbl_count.configure(text=f"Gambar: {n} / {self.max_images}")

    # ================================================================
    #  CLEAR ALL
    # ================================================================
    def clear_all(self):
        if not self.image_paths:
            return
        if not messagebox.askyesno("Konfirmasi", "Hapus semua gambar?"):
            return
        self.image_paths.clear()
        self.cv_images.clear()
        self.thumb_refs.clear()
        for w in self.img_list_frame.winfo_children():
            w.destroy()
        self._show_placeholder()
        self._update_count()
        self.progress.set(0)
        self.lbl_progress.configure(text="Siap memproses")
        self.lbl_status.configure(text="Semua gambar dihapus")

    # ================================================================
    #  PROCESS ALL
    # ================================================================
    def process_all(self):
        if not self.cv_images:
            messagebox.showwarning("Peringatan", "Upload gambar terlebih dahulu!")
            return

        total = len(self.cv_images)
        self.progress.set(0)
        self.lbl_progress.configure(text="Memulai proses...")
        self.lbl_status.configure(text="Memproses gambar...")
        self.update_idletasks()

        col_labels = ["Original", "Grayscale", "Binary", "Equalized", "Gaussian", "Canny Edge", "Segmented"]
        all_rows = []

        for i, img in enumerate(self.cv_images):
            self.lbl_progress.configure(text=f"Memproses {i + 1} / {total} ...")
            self.progress.set((i + 1) / total)
            self.update_idletasks()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            equalized = cv2.equalizeHist(gray)
            blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
            edges = cv2.Canny(blurred, 100, 200)
            _, segmented = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            to_bgr = lambda g: cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
            row = [
                cv2.resize(img, (CELL_W, CELL_H)),
                cv2.resize(to_bgr(gray), (CELL_W, CELL_H)),
                cv2.resize(to_bgr(binary), (CELL_W, CELL_H)),
                cv2.resize(to_bgr(equalized), (CELL_W, CELL_H)),
                cv2.resize(to_bgr(blurred), (CELL_W, CELL_H)),
                cv2.resize(to_bgr(edges), (CELL_W, CELL_H)),
                cv2.resize(to_bgr(segmented), (CELL_W, CELL_H)),
            ]
            all_rows.append(row)

        # Simpan file
        self._save_grid(all_rows, col_labels)
        self._save_individual()

        # Tampilkan di GUI
        self._display_grid(all_rows, col_labels)

        self.progress.set(1)
        self.lbl_progress.configure(text=f"Selesai! {total} gambar diproses.")
        self.lbl_status.configure(text=f"Proses selesai  |  {total} gambar  |  Hasil disimpan")

        messagebox.showinfo(
            "Proses Selesai",
            f"{total} gambar berhasil diproses!\n\n"
            "Tahapan:\n"
            "  1. Grayscale\n"
            "  2. Binary Threshold\n"
            "  3. Histogram Equalization\n"
            "  4. Gaussian Filter\n"
            "  5. Canny Edge Detection\n"
            "  6. Segmentasi Otsu\n\n"
            "Hasil disimpan di folder gambar.",
        )

    # ================================================================
    #  DISPLAY GRID (dalam GUI - presisi dengan grid layout)
    # ================================================================
    def _display_grid(self, all_rows, col_labels):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self._img_refs.clear()

        ncols = len(col_labels)
        nrows = len(all_rows)

        # Container utama
        table = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        table.pack(anchor="nw", padx=8, pady=8)

        # ---- HEADER ROW ----
        # Corner cell (No)
        corner = ctk.CTkFrame(table, fg_color=C["accent"], width=48, height=36, corner_radius=8)
        corner.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        corner.grid_propagate(False)
        ctk.CTkLabel(
            corner, text="No", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["text_bright"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Kolom header
        for c, label in enumerate(col_labels):
            hdr = ctk.CTkFrame(table, fg_color=C["col_label"], width=CELL_W + 8, height=36, corner_radius=8)
            hdr.grid(row=0, column=c + 1, padx=2, pady=2, sticky="nsew")
            hdr.grid_propagate(False)
            ctk.CTkLabel(
                hdr, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=C["text"],
            ).place(relx=0.5, rely=0.5, anchor="center")

        # ---- DATA ROWS ----
        for r, row_imgs in enumerate(all_rows):
            row_color = C["row_even"] if r % 2 == 0 else C["row_odd"]

            # Nomor
            num = ctk.CTkFrame(table, fg_color=row_color, width=48, height=CELL_H + 8, corner_radius=8)
            num.grid(row=r + 1, column=0, padx=2, pady=2, sticky="nsew")
            num.grid_propagate(False)
            ctk.CTkLabel(
                num, text=str(r + 1), font=ctk.CTkFont(size=14, weight="bold"),
                text_color=C["accent"],
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Gambar
            for c, cell_img in enumerate(row_imgs):
                cell = ctk.CTkFrame(
                    table, fg_color=row_color,
                    width=CELL_W + 8, height=CELL_H + 8, corner_radius=8,
                )
                cell.grid(row=r + 1, column=c + 1, padx=2, pady=2, sticky="nsew")
                cell.grid_propagate(False)

                rgb = cv2.cvtColor(cell_img, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                ctk_img = ctk.CTkImage(pil, size=(CELL_W, CELL_H))
                self._img_refs.append(ctk_img)

                ctk.CTkLabel(cell, image=ctk_img, text="").place(
                    relx=0.5, rely=0.5, anchor="center"
                )

        # ---- Footer ----
        out_path = os.path.join(os.path.dirname(self.image_paths[0]), "hasil_gabungan.jpg")
        foot = ctk.CTkFrame(self.scroll_frame, fg_color=C["card_light"], corner_radius=10)
        foot.pack(fill="x", padx=8, pady=(10, 8))
        ctk.CTkLabel(
            foot, text=f"Hasil disimpan:  {out_path}",
            font=ctk.CTkFont(size=11), text_color=C["success"], anchor="w",
            wraplength=900,
        ).pack(fill="x", padx=14, pady=10)

        self.lbl_title.configure(text=f"Hasil Pengolahan  --  {nrows} Gambar x {ncols} Tahapan")

    # ================================================================
    #  SAVE FILES
    # ================================================================
    def _save_grid(self, all_rows, col_labels):
        pad = 4
        lbl_h = 28
        rlw = 36
        ncols = len(col_labels)
        nrows = len(all_rows)

        W = rlw + ncols * (CELL_W + pad) + pad
        H = lbl_h + nrows * (CELL_H + pad) + pad
        canvas = np.full((H, W, 3), (26, 26, 46), dtype=np.uint8)

        for c, txt in enumerate(col_labels):
            x = rlw + pad + c * (CELL_W + pad)
            cv2.putText(canvas, txt, (x + 5, lbl_h - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (228, 228, 240), 1, cv2.LINE_AA)

        for r, row in enumerate(all_rows):
            y = lbl_h + pad + r * (CELL_H + pad)
            cv2.putText(canvas, str(r + 1), (10, y + CELL_H // 2 + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (108, 99, 255), 1, cv2.LINE_AA)
            for c, cell in enumerate(row):
                x = rlw + pad + c * (CELL_W + pad)
                canvas[y:y + CELL_H, x:x + CELL_W] = cell

        out = os.path.join(os.path.dirname(self.image_paths[0]), "hasil_gabungan.jpg")
        cv2.imwrite(out, canvas)

    def _save_individual(self):
        last = self.cv_images[-1]
        gray = cv2.cvtColor(last, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        eq = cv2.equalizeHist(gray)
        blur = cv2.GaussianBlur(eq, (5, 5), 0)
        edges = cv2.Canny(blur, 100, 200)
        _, seg = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        d = os.path.dirname(self.image_paths[0])
        cv2.imwrite(os.path.join(d, "hasil_1_grayscale.jpg"), gray)
        cv2.imwrite(os.path.join(d, "hasil_2_binary.jpg"), binary)
        cv2.imwrite(os.path.join(d, "hasil_3_equalized.jpg"), eq)
        cv2.imwrite(os.path.join(d, "hasil_4_gaussian.jpg"), blur)
        cv2.imwrite(os.path.join(d, "hasil_5_canny_edges.jpg"), edges)
        cv2.imwrite(os.path.join(d, "hasil_6_segmented.jpg"), seg)


# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    app = App()
    app.mainloop()