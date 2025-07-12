from email.message import EmailMessage
from pprint import pprint
import smtplib

import mailtrap as mt

from shopify import config


class EmailNotifier:

    def parse_verification_message(self, verification_token, firstname, lastname):
        return f"""
            Hi { firstname } {lastname or ""},

            Thank you for signing up! Please verify your email address by clicking the link below: 👉 { verification_token }

            This helps us keep your account secure and ensure you're able to receive important updates.

            If you did not request this, you can safely ignore this email.

            Best regards,
            Inventra Team
        """

    def parse_invitation_message(self, invitation_token, business_name):
        return f"""
            Hi from Inventra,

            The manager at { business_name }, has invited you to help manage their business.

            To accept the invitation and get started, please click the link below:

            👉 {config.MANAGER_INVITE_FORM_URL}/{invitation_token}

            If you weren’t expecting this invitation or don’t recognize the business, you can safely ignore this email.

            Looking forward to having you on board!

            Best regards,
            The Inventra Team
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
        msg = EmailMessage()
        msg["subject"] = subject
        msg["from"] = config.ADMIN_EMAIL
        msg["to"] = email

        msg.set_content(message)

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
