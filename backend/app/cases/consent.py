"""The privacy notice shown before a case is created. Plain words, one version number. Changing the text means a new version."""
CONSENT_VERSION = "2026-11-21-v1"

CONSENT_NOTICE = """What Nivaran does with your details
- We use the problem and details you give to find the company's official contact, write letters for you, and keep track of your case.
- Nothing is sent to a company until you read the letter, approve it, and tap Send.
- Your cases are stored encrypted. We never ask for, keep or type a card number, PIN, CVV, password or OTP. If you type one, it is removed.
- In this test version your text is read by outside AI services (Groq and Gemini) after payment details are removed. Do not write anything you would not want processed.
- You can delete a case at any time with "Delete my data for this case". A case with no activity for one year is deleted after a 48 hour warning.
- You can say no. Nivaran only starts a case after you agree below and confirm you are 18 or older."""


def notice() -> dict:
    return {"version": CONSENT_VERSION, "text": CONSENT_NOTICE}
