from pprint import pprint


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

    def parse_invitation_message(
        self, invitation_token, firstname, lastname, business_name
    ):
        return f"""
            Hi { firstname } { lastname or ""}

            The manager at { business_name }, has invited you to help manage their business.

            To accept the invitation and get started, please click the link below:

            👉 { invitation_token }

            If you weren’t expecting this invitation or don’t recognize the business, you can safely ignore this email.

            Looking forward to having you on board!

            Best regards,
            The Inventra Team
        """

    def send_verification_token(
        self, token: str, firstname: str, lastname: str, email: str
    ):
        message = self.parse_verification_message(token, firstname, lastname)
        self.send(message, email)

    def send_invitation_token(
        self, token: str, firstname: str, lastname: str, email: str, business_name: str
    ):
        message = self.parse_invitation_message(message)
        self.send(message, email)


class ConsoleEmailNotifier(EmailNotifier):
    def send(self, message: str, email: str):
        print()
        print(f"Intercepting Message For: {email}")
        pprint(message)
        print()


class SMTPEmailNotifier(EmailNotifier):
    pass


class MailGunEmailNotifier(EmailNotifier):
    pass
