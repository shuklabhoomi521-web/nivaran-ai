# Voice bot live test

Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).

| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |
|---|---|---|---|---|
| 1 English, two turns (Zomato, then the order number) (Indian-English voice (yours) then a computer-voice answer) | My Zomato order came 40 minutes late and the food was cold and I want a refund.<br>My order number is 4839201. | company=Zomato, category=food_delivery, goal=refund<br>company=Zomato, category=food_delivery, goal=refund; channel=email | Could you please provide your order ID?<br>I understand you want a refund from Zomato because your food arrived cold and fo | 8.7 s, 12.6 s |
