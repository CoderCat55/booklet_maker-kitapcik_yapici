import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_bytes
import io
import os

st.set_page_config(
    page_title="Booklet Maker",
    page_icon="📖",
    layout="centered"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }
        h1, h2, h3 {
            font-family: 'DM Serif Display', serif;
        }
        .stApp {
            background-color: #F7F4EF;
        }
        .block-container {
            padding-top: 3rem;
            max-width: 680px;
        }
        .upload-box {
            border: 2px dashed #C8B89A;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            background: #FFFDF9;
        }
        .stButton > button {
            background-color: #2C2C2C;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 2rem;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            font-weight: 500;
            width: 100%;
            transition: background 0.2s;
        }
        .stButton > button:hover {
            background-color: #444;
            color: white;
        }
        .stDownloadButton > button {
            background-color: #5C6E4A;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 2rem;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            font-weight: 500;
            width: 100%;
        }
        .stDownloadButton > button:hover {
            background-color: #4a5a39;
            color: white;
        }
        .info-card {
            background: #FFFDF9;
            border: 1px solid #E5DDD0;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #444;
        }
        .tag {
            display: inline-block;
            background: #EDE8DF;
            border-radius: 20px;
            padding: 2px 12px;
            font-size: 0.8rem;
            color: #555;
            margin-right: 4px;
        }
        hr {
            border: none;
            border-top: 1px solid #E5DDD0;
            margin: 1.5rem 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 📖 Booklet Maker")
st.markdown("Upload a PDF and get a print-ready booklet — covers included, pages imposed 2-up.")

st.markdown("<hr>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    reader = PdfReader(io.BytesIO(pdf_bytes))
    original_pages = len(reader.pages)

    st.markdown(f"""
        <div class='info-card'>
            <span class='tag'>📄 {original_pages} pages</span>
            <span class='tag'>📎 {uploaded_file.name}</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Generate Booklet"):
        with st.spinner("Processing your booklet..."):
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                page_width = reader.pages[0].mediabox.width
                page_height = reader.pages[0].mediabox.height

                # Add blank cover at beginning and end
                cover_writer = PdfWriter()
                cover_writer.add_blank_page(width=page_width, height=page_height)
                for page in reader.pages:
                    cover_writer.add_page(page)
                cover_writer.add_blank_page(width=page_width, height=page_height)
                cover_buf = io.BytesIO()
                cover_writer.write(cover_buf)
                cover_buf.seek(0)
                reader = PdfReader(cover_buf)

                n = len(reader.pages)

                # If odd, add blank page at the END
                if n % 2 != 0:
                    n += 1
                    w = PdfWriter()
                    for page in reader.pages:
                        w.add_page(page)
                    w.add_blank_page(width=page_width, height=page_height)
                    temp_buf = io.BytesIO()
                    w.write(temp_buf)
                    temp_buf.seek(0)
                    reader = PdfReader(temp_buf)

                # Build imposition array
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

                # Arrange pages
                writer = PdfWriter()
                for grup in array:
                    nn, bb, d = grup
                    page1 = reader.pages[nn - 1]
                    page2 = reader.pages[bb - 1]
                    if d == 0:
                        page1.rotate(180)
                        page2.rotate(180)
                    writer.add_page(page1)
                    writer.add_page(page2)

                arranged_buf = io.BytesIO()
                writer.write(arranged_buf)
                arranged_buf.seek(0)

                # 2-up imposition: place 2 pages side by side on one sheet
                arranged_reader = PdfReader(arranged_buf)
                sheet_width = float(page_width) * 2
                sheet_height = float(page_height)

                twoup_buffer = io.BytesIO()
                c = canvas.Canvas(twoup_buffer, pagesize=(sheet_width, sheet_height))

                pages = arranged_reader.pages
                progress = st.progress(0)
                total_sheets = (len(pages) + 1) // 2

                i = 0
                while i < len(pages):
                    # Left page
                    left_buf = io.BytesIO()
                    lw = PdfWriter()
                    lw.add_page(pages[i])
                    lw.write(left_buf)
                    left_buf.seek(0)
                    left_img = convert_from_bytes(left_buf.read(), dpi=150)[0]
                    c.drawImage(ImageReader(left_img), 0, 0,
                                width=float(page_width), height=float(page_height))

                    # Right page
                    if i + 1 < len(pages):
                        right_buf = io.BytesIO()
                        rw = PdfWriter()
                        rw.add_page(pages[i + 1])
                        rw.write(right_buf)
                        right_buf.seek(0)
                        right_img = convert_from_bytes(right_buf.read(), dpi=150)[0]
                        c.drawImage(ImageReader(right_img), float(page_width), 0,
                                    width=float(page_width), height=float(page_height))

                    c.showPage()
                    i += 2
                    progress.progress(min((i // 2) / total_sheets, 1.0))

                c.save()
                twoup_buffer.seek(0)
                result_bytes = twoup_buffer.read()

                st.success("✅ Booklet ready!")
                output_name = f"booklet_{uploaded_file.name}"
                st.download_button(
                    label="⬇ Download Booklet PDF",
                    data=result_bytes,
                    file_name=output_name,
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:0.8rem; color:#999; text-align:center;'>
        Print double-sided · Long-edge binding · Fold in half
    </div>
""", unsafe_allow_html=True)
