async def send_reset_password_email(email: str, token: str):
  print('RESET TOKEN', token)

async def send_verify_request_email(email: str, token: str):
  print('VERIFY TOKEN', token)