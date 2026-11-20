# -*- coding: utf-8 -*-
"""bookletmaker.ipynb
Original file is located at
    https://colab.research.google.com/drive/1cq09e424u-kZSS9QSBevfHxP1VbPi3I2
"""

# Local prerequisites (run ONCE in a terminal, not in this script):
#   pip install PyPDF2 reportlab pdf2image
# pdf2image also needs the Poppler binaries on PATH:
#   - Windows: https://github.com/oschwartz10612/poppler-windows/releases  (add bin\ to PATH)
#   - macOS:   brew install poppler
#   - Linux:   sudo apt install poppler-utils

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
import io
import os

# --- Local replacement for google.colab.files ------------------------------
try:
    from google.colab import files  # type: ignore  # Colab only
except ImportError:
    class _LocalFiles:
        @staticmethod
        def upload():
            paths = []
            try:
                from tkinter import Tk, filedialog
                root = Tk(); root.withdraw()
                paths = list(filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")]))
                root.destroy()
            except Exception:
                paths = []
            if not paths:
                p = input("PDF file path: ").strip().strip('"').strip("'")
                if p:
                    paths = [p]
            result = {}
            for p in paths:
                with open(p, "rb") as f:
                    data = f.read()
                base = os.path.basename(p)
                # Mimic Colab: uploaded files are written to the current dir
                with open(base, "wb") as f:
                    f.write(data)
                result[base] = data
            return result
        @staticmethod
        def download(path):
            print(f"Saved to: {os.path.abspath(path)}")
    files = _LocalFiles
# ---------------------------------------------------------------------------

def pdf_duzenle():
    # Kullanıcıdan PDF dosyasını yüklemesini iste
    uploaded = files.upload()
    mirrored = input("Mirror booklet? [y/N]: ").strip().lower() in ("y", "yes", "1", "true")
    covered = input("Add a cover booklet? [y/N]: ").strip().lower() in ("y", "yes", "1", "true")
    for input_pdf_path in uploaded.keys():

      # Çıktı dosyasının adını otomatik oluştur
      input_filename = os.path.basename(input_pdf_path)
      output_filename = f"uzunKenardanCevir_{input_filename}"
      output_pdf_path = output_filename  # Colab'da dosyalar geçici dizinde saklanır

      # PDF düzenleme işlemleri
      reader = PdfReader(input_pdf_path)
      page_width = reader.pages[0].mediabox.width
      page_height = reader.pages[0].mediabox.height

      if covered:    
        cover_writer = PdfWriter()
        cover_writer.add_blank_page(width=page_width, height=page_height)
        for page in reader.pages:
            cover_writer.add_page(page)
        cover_writer.add_blank_page(width=page_width, height=page_height)
        cover_temp = "cover_temp.pdf"
        with open(cover_temp, "wb") as f:
            cover_writer.write(f)
        reader = PdfReader(cover_temp)
          
      n = len(reader.pages)
      
      if n % 2 != 0:
          n += 1
          writer = PdfWriter()
          for page in reader.pages:
              writer.add_page(page)
          writer.add_blank_page(width=reader.pages[0].mediabox.width, height=reader.pages[0].mediabox.height)
          temp_pdf = "temp.pdf"
          with open(temp_pdf, "wb") as f:
              writer.write(f)
          reader = PdfReader(temp_pdf)

      m = n // 2
      b = 1
      array = []
      if mirrored:
          for y in range(0, m):
            if y % 2 == 0:
                bb = n - y
                nn = b + y
                d = 1
            else:
                nn = b + y
                bb = n - y
                d = 0
            array.append([nn, bb, d])
      else:
          for y in range(0, m):
            if y % 2 == 0:
                nn = n - y
                bb = b + y
                d = 1
            else:
                bb = b + y
                nn = n - y
                d = 0
            array.append([nn, bb, d])

      writer = PdfWriter()
      for grup in array:
          nn, bb, d = grup
          page_nn = nn - 1
          page_bb = bb - 1
          page1 = reader.pages[page_nn]
          page2 = reader.pages[page_bb]
          if d == 0:
              page1.rotate(180)
              page2.rotate(180)
          writer.add_page(page1)
          writer.add_page(page2)

      arranged_pdf = "arranged_temp.pdf"
      with open(arranged_pdf, "wb") as f:
          writer.write(f)

      # ADDITION: Save as 2 sheets for 1 page (2-up imposition) before downloading
      arranged_reader = PdfReader(arranged_pdf)
      sheet_width = float(page_width) * 2
      sheet_height = float(page_height)

      twoup_buffer = io.BytesIO()
      c = canvas.Canvas(twoup_buffer, pagesize=(sheet_width, sheet_height))

      pages = arranged_reader.pages
      i = 0
      while i < len(pages):
          # Write a two-page sheet: left page and right page side by side
          left_pdf_bytes = io.BytesIO()
          left_writer = PdfWriter()
          left_writer.add_page(pages[i])
          left_writer.write(left_pdf_bytes)
          left_pdf_bytes.seek(0)

          c.drawImage(
              __import__('reportlab.lib.utils', fromlist=['ImageReader']).ImageReader(
                  __import__('pdf2image', fromlist=['convert_from_bytes']).convert_from_bytes(
                      left_pdf_bytes.read(), dpi=150
                  )[0]
              ),
              0, 0, width=float(page_width), height=float(page_height)
          )

          if i + 1 < len(pages):
              right_pdf_bytes = io.BytesIO()
              right_writer = PdfWriter()
              right_writer.add_page(pages[i + 1])
              right_writer.write(right_pdf_bytes)
              right_pdf_bytes.seek(0)

              c.drawImage(
                  __import__('reportlab.lib.utils', fromlist=['ImageReader']).ImageReader(
                      __import__('pdf2image', fromlist=['convert_from_bytes']).convert_from_bytes(
                          right_pdf_bytes.read(), dpi=150
                      )[0]
                  ),
                  float(page_width), 0, width=float(page_width), height=float(page_height)
              )

          c.showPage()
          i += 2

      c.save()
      twoup_buffer.seek(0)
      with open(output_pdf_path, "wb") as f:
          f.write(twoup_buffer.read())

      # Düzenlenmiş dosyayı indirmek için link oluştur
      files.download(output_pdf_path)
      print(f"Düzenlenmiş PDF dosyası indirildi: {output_filename}")

# Programı çalıştır
pdf_duzenle()