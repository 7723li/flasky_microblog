import subprocess,os
os.chdir(os.getcwd())
print(os.getcwd())
man=subprocess.getoutput(r'python C:\Users\Administrator\Desktop\flasky\manage.py runserver --host 0.0.0.0')
print(man)