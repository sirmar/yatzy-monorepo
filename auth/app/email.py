from typing import Protocol


class EmailSender(Protocol):
  async def send_verification(self, email: str, token: str) -> None: ...
  async def send_password_reset(self, email: str, token: str) -> None: ...


class LogEmailSender:
  async def send_verification(self, email: str, token: str) -> None:
    print(f'[EMAIL] Verification token for {email}: {token}')

  async def send_password_reset(self, email: str, token: str) -> None:
    print(f'[EMAIL] Password reset token for {email}: {token}')
