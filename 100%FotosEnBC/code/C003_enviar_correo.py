
# This code is used as an example to send an email with an attachment
# print(''' - enviar_correo(to, subject, body, [attachment])''')

import win32com.client

def enviar_correo(to,subject='', body='', attachment=''):
  print('\n' + '-'*100 + '\n','Enviando email', '\n' + '-'*100)
  outlook = win32com.client.Dispatch('outlook.application')
  mail = outlook.CreateItem(0)
  mail.To = to
  mail.Subject = subject
  #mail.HTMLBody = '<h3>Cuerpo con h3</h3>'
  mail.Body = body

  if attachment!='':
    mail.Attachments.Add(attachment)
    #mail.Attachments.Add(attachment2)
    # mail.Attachments.Add(attachment3)
  #mail.CC = 'somebody@company.com'
  try:
    mail.Send()
  except:
    print('No se pudo enviar el email')
  print('Email enviado a',to)

'''
# Ejemplo de uso
path = r'S:\BI\16. DATA SCIENCE\4_Shared'
enviar_correo(to='frebollar@shasa.com', 
              subject='test_subject', 
              body='test_body', 
              attachment=path+r'\requirements.txt')
'''


