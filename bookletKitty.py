#!/usr/bin/env python3
"""
PDF imposition tool with a plain Tkinter UI.
Modes
Requires: pypdf   (pip install pypdf)
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from pypdf import PdfReader, PdfWriter, Transformation

try:
    from pypdf import PageObject
except ImportError:                     # very old pypdf
    PageObject = None

# A4 portrait in points
A4_W, A4_H = 595.276, 841.890

# --------------------------------------------------------------------------
# PDF helpers
# --------------------------------------------------------------------------
def make_blank(w, h):
    """Return a blank page of the given size."""
    if PageObject is not None and hasattr(PageObject, "create_blank_page"):
        return PageObject.create_blank_page(width=w, height=h)
    tmp = PdfWriter()
    return tmp.add_blank_page(width=w, height=h)


def place_page(sheet, src, x0, y0, box_w, box_h):
    """Scale `src` to fit the box (x0, y0, box_w, box_h) and center it."""
    if src is None:
        return
    src.transfer_rotation_to_content()
    left = float(src.mediabox.left)
    bottom = float(src.mediabox.bottom)
    w = float(src.mediabox.width)
    h = float(src.mediabox.height)
    s = min(box_w / w, box_h / h)
    tx = x0 + (box_w - w * s) / 2
    ty = y0 + (box_h - h * s) / 2
    t = Transformation().translate(-left, -bottom).scale(s, s).translate(tx, ty)
    sheet.merge_transformed_page(src, t)


def build_slides(input_path, output_path, pad_to_multiple_of_4=False):
    """2 slides per A4 portrait page, upper half and lower half."""
    reader = PdfReader(input_path)
    pages = list(reader.pages)
    if not pages:
        raise ValueError("PDF has no pages")

    n = len(pages)
    if pad_to_multiple_of_4:
        while n % 4:
            n += 1
    elif n % 2:
        n += 1

    half = A4_H / 2
    writer = PdfWriter()
    for i in range(n // 2):
        up = i + 1
        down = n - i
        sheet = writer.add_blank_page(width=A4_W, height=A4_H)
        place_page(sheet, pages[up - 1] if up <= len(pages) else None,
                   0, half, A4_W, half)
        place_page(sheet, pages[down - 1] if down <= len(pages) else None,
                   0, 0, A4_W, half)

    with open(output_path, "wb") as f:
        writer.write(f)


def build_booklet(input_path, output_path, mirrored=False, cover=False):
    reader = PdfReader(input_path)
    pages = list(reader.pages)
    if not pages:
        raise ValueError("PDF has no pages")

    pw = float(pages[0].mediabox.width)
    ph = float(pages[0].mediabox.height)

    if cover:
        pages = [make_blank(pw, ph)] + pages + [make_blank(pw, ph)]
    if len(pages) % 2:
        pages.append(make_blank(pw, ph))

    n = len(pages)
    m = n // 2

    arranged = []
    for y in range(m):
        if mirrored:
            nn, bb = 1 + y, n - y
        else:
            nn, bb = n - y, 1 + y
        d = 1 if y % 2 == 0 else 0     # 0 -> rotate both pages 180 degrees

        p1, p2 = pages[nn - 1], pages[bb - 1]
        if d == 0:
            p1.rotate(180)
            p2.rotate(180)
        arranged.append(p1)
        arranged.append(p2)

    writer = PdfWriter()
    for i in range(0, len(arranged), 2):
        sheet = writer.add_blank_page(width=pw * 2, height=ph)
        place_page(sheet, arranged[i], 0, 0, pw, ph)
        if i + 1 < len(arranged):
            place_page(sheet, arranged[i + 1], pw, 0, pw, ph)

    with open(output_path, "wb") as f:
        writer.write(f)

# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Booklet Kitty")
        self.resizable(True, False)
        self.files = []
        self.mode = tk.StringVar(value="booklet")
        self.mirror = tk.StringVar(value="no")
        self.cover = tk.StringVar(value="no")
        self.out_dir = tk.StringVar(value=os.getcwd())

        self._booklet_widgets = []
        self._build()

    # ---------------- layout ----------------
    def _build(self):
        root = ttk.Frame(self, padding=10)
        root.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        # 1) document type
        f_type = ttk.LabelFrame(root, text="1. Document type", padding=8)
        f_type.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Radiobutton(f_type, text="Slides",
                        value="slides", variable=self.mode,
                        command=self._sync).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(f_type, text="Booklet from pdf",
                        value="booklet", variable=self.mode,
                        command=self._sync).grid(row=1, column=0, sticky="w")

        # 2) booklet options
        f_opt = ttk.LabelFrame(root, text="2. Booklet options", padding=8)
        f_opt.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(f_opt, text="Mirror:").grid(row=0, column=0, sticky="w")
        r_no = ttk.Radiobutton(f_opt, text="No", value="no", variable=self.mirror)
        r_yes = ttk.Radiobutton(f_opt, text="Yes", value="yes", variable=self.mirror)
        r_no.grid(row=0, column=1, sticky="w", padx=(10, 0))
        r_yes.grid(row=0, column=2, sticky="w", padx=(10, 0))

        ttk.Label(f_opt, text="Cover:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        c_no = ttk.Radiobutton(f_opt, text="No", value="no", variable=self.cover)
        c_yes = ttk.Radiobutton(f_opt, text="Yes", value="yes", variable=self.cover)
        c_no.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(6, 0))
        c_yes.grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(6, 0))

        self._booklet_widgets = [r_no, r_yes, c_no, c_yes]

        # 3) input files
        f_files = ttk.LabelFrame(root, text="3. Input PDF files", padding=8)
        f_files.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        f_files.columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(f_files, height=5, selectmode="extended",
                                  activestyle="none")
        self.listbox.grid(row=0, column=0, sticky="ew", rowspan=3)
        sb = ttk.Scrollbar(f_files, orient="vertical",
                           command=self.listbox.yview)
        sb.grid(row=0, column=1, sticky="ns", rowspan=3)
        self.listbox.config(yscrollcommand=sb.set)

        ttk.Button(f_files, text="Add files…", command=self._add).grid(
            row=0, column=2, sticky="ew", padx=(8, 0))
        ttk.Button(f_files, text="Remove selected", command=self._remove).grid(
            row=1, column=2, sticky="ew", padx=(8, 0), pady=4)
        ttk.Button(f_files, text="Clear list", command=self._clear).grid(
            row=2, column=2, sticky="ew", padx=(8, 0))

        # 4) output folder
        f_out = ttk.LabelFrame(root, text="4. Output folder", padding=8)
        f_out.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        f_out.columnconfigure(0, weight=1)
        ttk.Entry(f_out, textvariable=self.out_dir).grid(row=0, column=0, sticky="ew")
        ttk.Button(f_out, text="Browse…", command=self._browse).grid(
            row=0, column=1, padx=(8, 0))

        # run
        bar = ttk.Frame(root)
        bar.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        bar.columnconfigure(0, weight=1)
        self.run_btn = ttk.Button(bar, text="Run", command=self._run)
        self.run_btn.grid(row=0, column=0, sticky="ew")
        ttk.Button(bar, text="Quit", command=self.destroy).grid(
            row=0, column=1, padx=(8, 0))

        # log
        f_log = ttk.LabelFrame(root, text="Log", padding=8)
        f_log.grid(row=5, column=0, sticky="nsew")
        f_log.columnconfigure(0, weight=1)
        self.log = tk.Text(f_log, height=9, width=78, state="disabled", wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")
        lsb = ttk.Scrollbar(f_log, orient="vertical", command=self.log.yview)
        lsb.grid(row=0, column=1, sticky="ns")
        self.log.config(yscrollcommand=lsb.set)

        self._sync()

    # ---------------- state ----------------
    def _sync(self):
        """Enable booklet options only in booklet mode."""
        state = "normal" if self.mode.get() == "booklet" else "disabled"
        for w in self._booklet_widgets:
            w.configure(state=state)

    # ---------------- file list ----------------
    def _add(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF files", filetypes=[("PDF files", "*.pdf")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", p)

    def _remove(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)
            del self.files[i]

    def _clear(self):
        self.listbox.delete(0, "end")
        self.files.clear()

    def _browse(self):
        d = filedialog.askdirectory(title="Choose output folder",
                                    initialdir=self.out_dir.get())
        if d:
            self.out_dir.set(d)

    # ---------------- logging ----------------
    def _log(self, msg):
        self.after(0, self._append, msg)

    def _append(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    # ---------------- run ----------------
    def _run(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add at least one PDF file.")
            return
        out_dir = self.out_dir.get().strip() or os.getcwd()
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Output folder", str(e))
            return

        args = (list(self.files), out_dir, self.mode.get(),
                self.mirror.get() == "yes", self.cover.get() == "yes")

        self.run_btn.configure(state="disabled")
        self._log("")
        self._log(f"--- starting: mode={args[2]}, mirror={args[3]}, "
                  f"cover={args[4]} ---")
        threading.Thread(target=self._worker, args=args, daemon=True).start()

    def _worker(self, files, out_dir, mode, mirrored, cover):
        ok = 0
        for path in files:
            stem = os.path.splitext(os.path.basename(path))[0]
            if mode == "slides":
                out = os.path.join(out_dir, f"duzenlenmis_{stem}.pdf")
            else:
                out = os.path.join(out_dir, f"uzunKenardanCevir_{stem}.pdf")
            try:
                if mode == "slides":
                    build_slides(path, out)
                else:
                    build_booklet(path, out, mirrored=mirrored, cover=cover)
                ok += 1
                self._log(f"OK    {out}")
            except Exception as e:                      # noqa: BLE001
                self._log(f"FAIL  {path}: {e}")
        self._log(f"--- done: {ok}/{len(files)} written to {out_dir} ---")
        self.after(0, lambda: self.run_btn.configure(state="normal"))


if __name__ == "__main__":
    App().mainloop()
