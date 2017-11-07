import os
#os.chdir(os.getcwd()+r'\app')

with open(__file__.split('\\')[-1].replace('py','txt'),'w') as f:
    f.write(str(os.popen('tree /f').read()))
