# Voice bot live test

Recorded audio is played into the running voice server over real WebRTC (like a browser). Computer voices are marked. Latency = from the end of the person's sentence to the first sound the bot makes in reply (measured on the audio the client receives).

| Scenario | Heard (speech-to-text) | Understood | Bot said | Delay to first sound |
|---|---|---|---|---|
| 1 English, two turns (Zomato, then the order number) (Indian-English voice (yours) then a computer-voice answer) | My Zomato order came 40 minutes late and the food was cold and I want a refund.<br>My order number is 4839201. | company=Zomato, category=food_delivery, goal=refund | Could you please provide your order ID? | 7.5 s, 7.6 s |
| 2 Hinglish, one turn (Amazon, order number given) (your voice) | Order number 4839201 है Amazon ने गलत size की कुर्ती भेज दी। | company=Amazon, category=ecommerce, goal=replace | Kya aapko is item ke liye replacement chahiye ya refund? | 7.8 s |
| 3 Hindi (Zomato) (computer voice) | मेरा ज़ोमैटो का खाना ठंडा आया, मुझे पैसे वापस चाहिए। |  |  | 7.8 s |
| 4 Tamil (Swiggy) (computer voice) | என் ஸ்விக்கி ஆர்டர் குளிர்ந்து வந்தது. எனக்கு பணம் திரும்ப வேண்டும். | company=Swiggy, category=food_delivery, goal=refund | தயவுசெய்து உங்கள் ஆர்டர் ஐடி (Order ID) என்னவென்று கூற முடியுமா? | 7.9 s |
| 5 Talking over the bot (barge-in) (speech starts 3 s in, while the greeting is still playing) | My Zomato order came 40 minutes late and the food was cold and I want a refund. | company=Zomato, category=food_delivery, goal=refund | Could you please share your order ID? | 7.7 s |
| 6 Card number said aloud (computer voice) | My Swiggy order came cold and I want a refund. My card number is [CARD NUMBER REMOVED]. | company=Swiggy, category=food_delivery, goal=refund (private data removed: card_number) | Could you please provide your order ID? | 7.9 s |
