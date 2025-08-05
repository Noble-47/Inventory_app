from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pprint import pprint
import smtplib

import mailtrap as mt

from shopify import config


class EmailNotifier:

    def parse_verification_message(self, verification_token, firstname, lastname):
        return f"""
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8">
                <title>Email Verification</title>
                <style>
                  body {{
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                    padding: 20px;
                    color: #333;
                  }}
                  .container {{
                    max-width: 600px;
                    margin: auto;
                    background: #fff;
                    padding: 30px;
                    border-radius: 6px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                  }}
                  .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    margin-top: 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                  }}
                  .footer {{
                    margin-top: 30px;
                    font-size: 13px;
                    color: #888;
                  }}
                </style>
              </head>
              <body>
                <div class="container">
                  <p>Hi {firstname} {lastname or ""},</p>
                  <p>Thank you for signing up! To complete your registration, please verify your email address by clicking the button below:</p>
                  <p>
                    <a href="{config.SERVER_ROOT_URL}/accounts/verification/{verification_token}" class="button">
                      Verify Email
                    </a>
                  </p>
                  <p>This helps us keep your account secure and ensures you receive important updates from us.</p>
                  <p>If you did not request this, you can safely ignore this email.</p>
                  <div class="footer">
                    <p>Best regards,<br>Inventra Team</p>
                  </div>
                </div>
              </body>
            </html>
        """

    def parse_invitation_message(self, invitation_token, business_name):
        return f"""
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8">
                <title>Manager Invitation</title>
                <style>
                  body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                    color: #333;
                  }}
                  .container {{
                    max-width: 600px;
                    margin: auto;
                    background: #ffffff;
                    padding: 30px;
                    border-radius: 6px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                  }}
                  .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    margin-top: 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                  }}
                  .footer {{
                    margin-top: 30px;
                    font-size: 13px;
                    color: #888;
                  }}
                </style>
              </head>
              <body>
                <div class="container">
                  <p>Hi from Inventra,</p>
                  <p>The manager at <strong>{business_name}</strong> has invited you to help manage their business.</p>
                  <p>To accept the invitation and get started, please click the button below:</p>
                  <p>
                    <a href="{config.FRONTEND_ROOT_URL}/manager-invite/{invitation_token}/accept" class="button">
                      Accept Invitation
                    </a>
                  </p>
                  <p>If you weren’t expecting this invitation or don’t recognize the business, feel free to ignore this message.</p>
                  <div class="footer">
                    <p>Looking forward to having you on board!<br><br>
                    Best regards,<br>
                    The Inventra Team</p>
                  </div>
                </div>
              </body>
            </html>
        """

    def send_verification_email(
        self, token: str, firstname: str, lastname: str, email: str
    ):
        message = self.parse_verification_message(token, firstname, lastname)
        self.send(message, email, subject="Verify Your Email.")

    def send_invite_email(self, token: str, email: str, business_name: str):
        message = self.parse_invitation_message(
            invitation_token=token, business_name=business_name
        )
        self.send(message, email, subject=f"Manager Invite From {business_name}")


class ConsoleLog(EmailNotifier):
    def send(self, message: str, email: str, subject):
        print()
        print(f"Intercepting Message For: {email}")
        pprint(message)
        print()


class MailTrap(EmailNotifier):

    def production_send(self, message: str, email: str, subject: str):
        mail = mt.Mail(
            sender=mt.Address(email=config.ADMIN_EMAIL, name=config.ADMIN_NAME),
            to=[mt.Address(email)],
            subject=subject,
            text=message,
        )

        client = mt.MailtrapClient(token=config.EMAIL_PROVIDER_KEY)
        client.send(mail)

    def development_send(self, message: str, email: str, subject: str):
        msg = MIMEMultipart()
        msg["subject"] = subject
        msg["from"] = config.ADMIN_EMAIL
        msg["to"] = email
        msg.attach(MIMEText(message, "html"))

        # msg.set_content(message)

        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("b14bc5e7d1c73c", "3fb3df54ac1244")
            server.send_message(msg)

    def send(self, message: str, email: str, subject: str):
        if config.DEBUG:
            self.development_send(message, email, subject)
        else:
            self.production_send(message, email, subject)


class MailGun(EmailNotifier):
    pass
