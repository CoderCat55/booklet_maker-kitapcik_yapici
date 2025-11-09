# Kullanıcıdan n değerini al
n = int(input("PDF'in sayfa sayısı kaç? "))

# n tek ise n=n+1
if n % 2 == 0:
    n = n
else:
    n = n + 1

m = n / 2
b = 1
#d sayfanın düz mü yoksa ters mi olacağı 1=düz   0=ters

array = []

for y in range(0, int(m)):
    if y % 2 == 0:  # y çift 
        nn = n - y
        bb = b + y
        d=1
        array.append([nn, bb, d])
    else:  # y tek
        bb = b + y
        nn = n - y
        d=0
        array.append([nn, bb ,d])

print(array)