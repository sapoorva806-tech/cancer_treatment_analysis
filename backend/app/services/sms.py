"""
Mock SMS sender — prints the OTP to the console/logs instead of sending a
real text message. Swap the body of send_otp() for a real provider
(Twilio, AWS SNS, etc.) when you're ready to send actual SMS.
"""


def send_otp(phone_number: str, code: str) -> None:
    print(f"\n{'='*50}")
    print(f"[MOCK SMS] To: {phone_number}")
    print(f"[MOCK SMS] Your Hodgkin Risk Platform verification code is: {code}")
    print(f"[MOCK SMS] This code expires in 5 minutes.")
    print(f"{'='*50}\n")