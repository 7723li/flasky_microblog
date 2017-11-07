from threading import Thread
from flask import current_app, render_template
import smtplib
from email.mime.text import MIMEText
#from flask_mail import Message
#from . import mail

def send_async_email(app,s,msg,sender,to):
    try:
        s.sendmail(sender, to, msg.as_string())
    except smtplib.SMTPDataError as e:#554 DT:SPM 垃圾邮件
        pass
    
def send_email(to, subject, template, **kwargs):
    host=current_app.config['MAIL_SERVER']
    port=current_app.config['MAIL_PORT']
    
    sender=current_app.config['FLASKY_MAIL_SENDER']
    #print(sender)
    pwd=current_app.config['MAIL_PASSWORD']

    with current_app.app_context():#激活程序上下文
        html = render_template(template + '.html', **kwargs)#正文
    msg = MIMEText(html, 'html')
    msg['subject'] = current_app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject#主题
    
    msg['from'] = current_app.config['FLASKY_MAIL_SENDER']
    msg['to'] = to#to
    try:  
        s = smtplib.SMTP(host, port)  
        s.login(sender, pwd)
        thr=Thread(target=send_async_email,args=[current_app,s,msg,sender,to])
        thr.start()
        return thr
    except smtplib.SMTPException:  
        pass
