import subprocess
print ('start')
p1 = subprocess.Popen(["python", "main_rotate.py", "JuznaSrbija0052_crop.tif"])
p2 = subprocess.Popen(["python", "main_rotate.py", "JuznaSrbija0051_crop.tif"])
p3 = subprocess.Popen(["python", "main_rotate.py", "JuznaSrbija0054_crop.tif"])

p1.wait()
p2.wait()
p3.wait()
print ('complete')

p1 = subprocess.Popen(["python", "main_rotate.py", "Vasojevici0033_crop.tif"])
p2 = subprocess.Popen(["python", "main_rotate.py", "Vasojevici0035_crop.tif"])
p3 = subprocess.Popen(["python", "main_rotate.py", "Vasojevici0034_crop.tif"])

p1.wait()
p2.wait()
p3.wait()
print ('complete2')
