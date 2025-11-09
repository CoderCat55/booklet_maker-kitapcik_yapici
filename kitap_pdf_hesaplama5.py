from PyPDF2 import PdfReader, PdfWriter
import os

"""Bu programda kaydedilmiş pdf'i yazıcı ayarlarında her sayfada 2 sayfa olacak şekilde ayarla dersen eğer çalışıyor """

def pdf_duzenle():
    # Kullanıcıdan girdi PDF dosyasının yolunu al
    input_pdf_path = input("Lütfen düzenlemek istediğiniz PDF dosyasının yolunu tırnak içinde girin (örnek: \"C:/Belgeler/ornek.pdf\"): ").strip('"')

    # Çıktı dosyasının adını otomatik oluştur
    input_filename = os.path.basename(input_pdf_path)
    output_filename = f"duzenlenmis_{input_filename}"
    output_pdf_path = os.path.join(os.path.dirname(input_pdf_path), output_filename)

    # PDF düzenleme işlemleri
    reader = PdfReader(input_pdf_path)
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

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    print(f"Düzenlenmiş PDF dosyası oluşturuldu: {output_pdf_path}")

# Programı çalıştır
pdf_duzenle()
