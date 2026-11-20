# Booklet Maker - Kitapçık Yapıcı

### Amaç
A4 boyutundaki PDF'leri **basılabilir kitapçık** haline getirir. Aslında **A4 PDF'leri A5 boyutunda kitap** olarak kullanmanızı sağlar.

---

### Algoritma Bilgisi
- `pdf_hesaplama_4` algoritmasını içerir. *(Meraklıları için)*
### Asıl Program
- **`pdf_hesaplama_5.py`** *(Bilgisayarda offline çalıştırmak için)*
  - **Gereksinim:** `PyPDF2` kütüphanesi
  - **Kurulum:** `pip install PyPDF2`
----

### Colab Linki
Bilgisayarda **online çalıştırmak** için:
🔗 [https://colab.research.google.com/drive/1cq09e424u-kZSS9QSBevfHxP1VbPi3I2?usp=sharing](https://colab.research.google.com/drive/1cq09e424u-kZSS9QSBevfHxP1VbPi3I2?usp=sharing)
  - **Arkalı önlü** uzun kenardan çeivrmeli basılacak şekilde yazıcıya gönderilmelidir.
  - yazıcıdan çıktı aldıktan sonra elinizdeki kağıt destesini yazıcıdan çıktığı haliyle ortadan 2 ye katlayın. elinizde a5 boyutunda bir kitapçık olacak
  - orta sayfayı birbirine bantlayın
Bu linkte eğer kağıtları ortadan keserseniz kestiğiniz kağıttan onları yapıştırarak kitabı ciltleyebilirsiniz fakat keserken yamukluklar yüzünden yapıştırıcı tam tutmayabiliyor bu nedenle aynı programın aynalı versiyonunu hazırladım. Kitabı ciltlemek isteyenler aynı şekilde kağıtları ortadan kesip kağıdın kesilmemiş kenarından yapıştırıcıyla veya delik açarak ciltleyebilir.
https://colab.research.google.com/drive/1uJLiNVE7H5YAT1MVHyikR14YJHjg_0gw?usp=sharing

Slyatlar için https://colab.research.google.com/drive/1hu0KW_lKz9n2OnSdV5c6OVvzXycRqb2g?usp=sharing
  - çıkan pdfyi arkalı önlü,uzun kenardan çevirmeli çıktı alın
  - kağıdın ortasından kısa kenara paralel olacak şekilde kesin
  - kesilen parçalardan altta olanı alın ters çevirin ve kesilen üst parçanın arkasına ekleyin.
