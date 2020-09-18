
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "davidoliver5086@gmail.com"
password = "Metal0121!"

# Create a secure SSL context
context = ssl.create_default_context()

# Create the plain-text and HTML version of your message
text = """\
ユーザー様、
予約が{0}しました。
{1}"""
html = """\
<html>
  <body>
    <p>ユーザー様、<br>       
       予約が{0}しました。<br>
       {1}
    </p>
  </body>
</html>
"""

def sendMail(result, reason):

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here

        receiver_email = "dantes0121@hotmail.com"

        # prepare message content
        message = MIMEMultipart("alternative")
        message["Subject"] = "自動予約"
        message["From"] = sender_email
        message["To"] = receiver_email
        
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text.format(result, reason), "plain")
        part2 = MIMEText(html.format(result, reason), "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 

def main():
    sendMail("成功", "楽しい時間をお過ごしください。")


if __name__ == '__main__':
    main()