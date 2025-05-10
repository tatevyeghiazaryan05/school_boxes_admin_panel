a = "  hello  ,  bonjure  ,  barev  "
b=a.split(",")
new_b=[]
for i in b:
    i=i.strip()
    new_b.append(i)
print(new_b)
