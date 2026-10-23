# Voice bot live test

Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).

| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |
|---|---|---|---|---|
| 1 English, two turns (Zomato, then the order number) (Indian-English voice (yours) then a computer-voice answer) | My Zomato order came 40 minutes late and the food was cold and I want a refund.<br>My order number is 4839201. | company=Zomato, category=food_delivery, goal=refund<br>company=Zomato, category=food_delivery, goal=refund; channel=email | Please share your order ID.<br>I see your Zomato order #4839201 was late and cold, and you’d like a refund. I c | 4.7 s, 7.2 s |
| 2 Hinglish, one turn (Amazon, order number given) (your voice) | Order number 4839201 है Amazon ने गलत size की कुर्ती भेज दी। | company=Amazon, category=ecommerce, goal=replace | कृपया सही साइज बताइए? | 3.4 s |
| 3 Hindi (Zomato) (computer voice) | मेरा ज़ोमैटो का खाना ठंडा आया, मुझे पैसे वापस चाहिए। | company=Zomato, category=food_delivery, goal=refund | कृपया अपना ऑर्डर आईडी बताइए। | 3.6 s |
| 4 Tamil (Swiggy) (computer voice) | என் ஸ்விக்கி ஆர்டர் குளிர்ந்து வந்தது. எனக்கு பணம் திரும்ப வேண்டும். | company=Swiggy, category=food_delivery, goal=refund | தயவுசெய்து உங்கள் ஆர்டர் ஐடி (order ID) வழங்க முடியுமா? | 5.0 s |
| 5 Talking over the bot (barge-in) (speech starts 3 s in, while the greeting is still playing) | My Zomato order came 40 minutes late and the food was cold and I want a refund. | company=Zomato, category=food_delivery, goal=refund | Please provide the order ID for your Zomato order. | 4.9 s |
| 6 Card number said aloud (computer voice) | My Swiggy order came cold and I want a refund. My card number is [CARD NUMBER REMOVED]. | company=Swiggy, category=food_delivery, goal=refund (private data removed: card_number) | Please provide the order ID for your Swiggy order. | 3.8 s |
