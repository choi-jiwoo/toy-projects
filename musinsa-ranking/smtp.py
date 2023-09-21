from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from exception import EmptyUserInfoException
import util

class Smtp:

    def __init__(self, address: str, password: str) -> None:
        self.address = address
        self.password = password

        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.ehlo()
        self.smtp.starttls()

    @property
    def mail_address(self) -> str:
        return self._mail_address

    @mail_address.setter
    def mail_address(self, address: str) -> None:
        if address is None:
            raise EmptyUserInfoException('No user info is submitted.')
        self._mail_address = address

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        if password is None:
            raise EmptyUserInfoException('No user info is submitted.')
        self._password = password

    def send_mail(self, receiver: str, content: str) -> None:
        now = self.current_time()
        msg = MIMEMultipart()
        msg['Subject'] = f'무신사 스토어 {now} 검색어 랭킹'
        html_content = util.to_html(content, now)
        body = MIMEText(html_content, 'html')
        msg.attach(body)
        msg['To'] = receiver

        self.smtp.login(self.address, self.password)
        self.smtp.sendmail(self.address, receiver, msg.as_string())

    @staticmethod
    def current_time() -> datetime:
        now = datetime.now()
        now = now.strftime('%Y %m %d %H시')  # YYYY MM DD 00시 날짜 포맷
        return now

    def __repr__(self):
        return f'Email("{self.address}", "{self.password}")'

    def __del__(self):
        self.smtp.quit()
