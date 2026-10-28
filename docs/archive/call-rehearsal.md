# Practice call (pretend company, no real phone)

A pretend company line (menu, hold music, an agent) called our phone bot over the same websocket Twilio uses. Computer voices from the Mac. Speech-to-text, brain and voice are the real ones configured in .env.

Result: {"menu_delay": [13.2, 0.0], "menu": ["1", "1"], "answer1_delay": 13.3, "answer2_delay": 13.2, "otp_delay": 26.5, "goodbye_delay": 28.8}

## What the bot's side logged

- `14:40:48` **info**: phone call connected (en-IN)
- `14:40:48` **AI said**: Hello. I am an AI assistant calling on behalf of a customer about Swiggy. May I explain the problem?
- `14:41:25` **agent (heard)**: Welcome customer care. Press 1 for order issues, press 2 for payments, press 3 for anything else.
- `14:41:26` **info**: pressed keypad: 1
- `14:41:43` **agent (heard)**: For a late or cold order press 1, for missing items press 2, to return to the main menu press 9.
- `14:41:43` **info**: pressed keypad: 1
- `14:41:45` **agent (heard)**: Please hold while we connect you to an agent.
- `14:41:46` **AI said**: Thank you.
- `14:41:48` **info**: on hold: waiting quietly
- `14:41:57` **info**: off hold: someone is talking again
- `14:42:11` **agent (heard)**: Hello, this is priya from Swiggy support. How can I help you today?
- `14:42:12` **AI said**: Hello Priya, the order 4839201 arrived cold and the customer has not received a refund.
- `14:42:12` **AI said**: We would like a refund to be processed and a reference number for this request, please.
- `14:42:42` **agent (heard)**: Can you give me the order ID, please?
- `14:42:43` **AI said**: The order ID is 4839201.
- `14:43:22` **agent (heard)**: To verify, please tell me the OTP you received on your phone.
- `14:43:22` **AI said**: I am sorry, I cannot share or accept card numbers, PINs, passwords or one-time codes on a call. The customer will handle that themselves.
- `14:44:12` **agent (heard)**: Ok, I have raised a refund for you. Your ticket number is T555. Is there anything else?
- `14:44:13` **AI said**: Thank you, Priya.
- `14:44:13` **AI said**: That's all we needed.
- `14:44:13` **AI said**: Have a good day.
- `14:44:13` **info**: call ended by the AI
- `14:44:21` **info**: line closed
- `14:44:22` **info**: Sarvam credit used in this session: about Rs 1.01; about Rs 32.8 left (estimate; level: ok)
