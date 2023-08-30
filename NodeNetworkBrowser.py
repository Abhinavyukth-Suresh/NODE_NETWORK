import time

with open("browserCheck" , "w") as w:
    w.write("1")
 
time.sleep(10)

with open("browserCheck" , "w") as w:
    w.write("0")
