# Voice bot live test

Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).

| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |
|---|---|---|---|---|
| 7 Auto: English first, then switches to Hindi (language switch: the second answer must be in Hindi) | My Zomato order came 40 minutes late and the food was cold and I want a refund.<br>My Zomato ka Khana Thanda Aaya, Mujhe PaiseWapas CHahiye. | company=Zomato, category=food_delivery, goal=refund<br>company=Zomato, category=food_delivery, goal=refund | Could you please provide the order ID?<br>Kripya apna order ID batayenge? | 16.0 s, 6.0 s |
| 8 Auto: Tamil first, then switches to English (language switch: the second answer must be in English) | என் Swiggy order குளிர்ந்து வந்தது. எனக்கு பணம் திரும்ப வேண்டும்.<br>My order number is 4839201. | company=Swiggy, category=food_delivery, goal=refund<br>company=Swiggy, category=food_delivery, goal=refund; channel=email | தயவுசெய்து உங்கள் order ID-ஐ வழங்க முடியுமா?<br>I understand your Swiggy order arrived cold and you want a refund. I can email S | 4.9 s, 15.4 s |
