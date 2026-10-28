# Voice bot live test

Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).

| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |
|---|---|---|---|---|
| 9 Tamil chosen on the page, but the person speaks English (the page language is only the starting language: answers must be in English) | My Zomato order came 40 minutes late and the food was cold and I want a refund.<br>My order number is 4839201. | company=Zomato, category=food_delivery, goal=refund<br>company=Zomato, category=food_delivery, goal=refund; channel=email | Could you please provide the order ID?<br>I understand you ordered from Zomato, the food was cold and late, and you want a | 14.5 s, 14.4 s |
