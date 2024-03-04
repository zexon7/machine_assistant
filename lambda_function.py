import json
from datetime import date
import datetime
import pymysql
import smtplib
from email.message import EmailMessage

today = date.today()
conn = pymysql.connect(
        host= '', 
        port = 3306,
        user = 'admin', 
        password = '',
        db = 'sys'
        )
cur=conn.cursor()

# 更新維修日期
sql="UPDATE maintain_schedule "\
    "SET "\
    "maintain_date = next_maintain, "\
    "next_maintain = DATE_ADD(next_maintain , INTERVAL day_diff DAY) "\
    "WHERE machine_id = machine_id AND maintain_date<(%s)"
cur.execute(sql, today)
conn.commit()

sql = "SELECT machine_id,email,maintain_date FROM maintain_schedule WHERE maintain_date=(%s)"
cur.execute(sql, (today+datetime.timedelta(days=1)))
conn.commit()
rows = cur.fetchall()
sql = "SELECT machine_id,email,next_maintain FROM maintain_schedule WHERE next_maintain=(%s)"
cur.execute(sql, (today+datetime.timedelta(days=1)))
conn.commit()
rows = rows + cur.fetchall()

d = {}
for r in rows:
	d[r[0]] = [r[1],r[2]] # machine_id = [email, maintain_date/next_maintain]
	
k = list(d.keys())

def lambda_handler(event, context):
    
    if k:
        for machine_id in k:
            send_email(machine_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully sent email from Lambda using Amazon SES')
    }
   
def send_email(machine_id):
    gmail_user = ''
    gmail_app_password = ''
    
    msg = EmailMessage()
    msg['Subject'] = 'Machine Notification'
    msg['From'] = gmail_user
    msg['To'] = d[machine_id][0]
    msg.set_content('Please maintain your machine ' + machine_id + ' on '+ str(d[machine_id][1]))
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        #server.sendmail(sent_from, sent_to, email_text)
        server.send_message(msg)
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)