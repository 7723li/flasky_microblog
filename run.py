import subprocess
import os
import re
os.chdir(os.getcwd())
path = os.getcwd()
print(path)

while True:
    man=subprocess.getoutput(r'python {}\manage.py runserver --host 0.0.0.0'.format(path))
    module = re.findall("No module named '(.*?)'",man)[0]
    print(module)
    if(module == None):
        break
    else:
        subprocess.getoutput(r'pip install {}'.format(module))

print('Ready..')
print(subprocess.getoutput(r'python {}\manage.py runserver --host 0.0.0.0'.format(path)))
