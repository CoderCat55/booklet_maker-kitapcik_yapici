input: landscape pdf slides or pttx slides
output : pdf 
goal: print lanscape pdf files as a booklet
pdf page: A4
each pdf page contains: pageup(upper half of the page) , pagedown(lowe half of the page)
variables: 
b = default 1 (the first page  of input pdf)
n = last page of input pdf
if n is odd n= n+1

for i in range (0,n+1,1):
  pageup=b+i
  pagedown=n-i

propmpt:
use the information above to replace the current collab notebook's pdf algorithm.
keep other functions same like automatic pdf saving etc.

