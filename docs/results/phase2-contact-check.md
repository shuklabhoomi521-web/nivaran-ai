# Phase 2: contact check on the 30 problems

Uses the AI's saved answers from the real Phase 1 run (no new API calls). Contacts come only from the verified directory.

- Right company matched in the directory (or correctly no company): **30/30**
- Problems with a named company that also have at least one verified contact: **25/25**
- Problems with no company that were correctly left for a question: **5**

| Problem | Expected company | AI company | Channels available | Contact we would use | Result |
|---|---|---|---|---|---|
| en-01 | Swiggy | Swiggy | email, complaint | complaint grievances@swiggy.in | OK |
| en-02 | Amazon | Amazon | email, complaint | complaint grievance-officer@amazon.in | OK |
| en-03 | Airtel | Airtel | call | call 198 | OK |
| en-04 | IndiGo | IndiGo | call, email, complaint | call 0124-4973838; email customer.experience@goindigo.in; complaint nodalofficer@goindigo.in | OK |
| en-05 | (none) | (none) | - | - | OK: no company, so the AI asks a question and no contact is used |
| en-06 | Ola | Ola | email, complaint | complaint grievance@olacabs.com | OK |
| en-07 | Myntra | Myntra | email, complaint | complaint customergrievance@myntra.com | OK |
| hi-01 | Zomato | Zomato | email, complaint | email order@zomato.com; complaint grievance@zomato.com | OK |
| hi-02 | IRCTC | IRCTC | call, email | call 14646; email etickets@irctc.co.in | OK |
| hi-03 | PhonePe | PhonePe | call | call 080-68727374 | OK |
| hi-04 | LIC | LIC | call, email, complaint | call 022 6827 6827; complaint co_complaints@licindia.com | OK |
| hi-05 | (none) | (none) | - | - | OK: no company, so the AI asks a question and no contact is used |
| hi-06 | Samsung | Samsung | call | call 1800 5 7267864 | OK |
| ta-01 | Flipkart | Flipkart | email, complaint | complaint grievance.officer@flipkart.com | OK |
| ta-02 | Jio | Jio | call, email | call 198; email care@jio.com | OK |
| ta-03 | Uber | Uber | call, email, complaint | call +91 891 451 2030; complaint grievanceredressaloffice@uber.com | OK |
| ta-04 | Air India | Air India | call, email, complaint | call +91 116 932 9333; complaint nodalofficer@airindia.com | OK |
| ta-05 | BSNL | BSNL | call | call 1800-4444 | OK |
| ta-06 | Swiggy | Swiggy | email, complaint | complaint grievances@swiggy.in | OK |
| ta-07 | TNEB | TNEB | call | call 94987 94987 | OK |
| hg-01 | Meesho | Meesho | email, complaint | complaint legalsupport@meesho.com | OK |
| hg-02 | Paytm | Paytm | call, email, complaint | call 0120-4440440; complaint grievanceofficer@paytm.com | OK |
| hg-03 | Rapido | Rapido | email, complaint | email shoutout@rapido.bike; complaint nodalofficer@rapido.bike | OK |
| hg-04 | Star Health | Star Health | call, email, complaint | call 044 4366 4600; complaint support@starhealth.in | OK |
| hg-05 | (none) | (none) | - | - | OK: no company, so the AI asks a question and no contact is used |
| f-01 | Zomato | Zomato | email, complaint | email order@zomato.com; complaint grievance@zomato.com | OK |
| f-02 | Amazon | Amazon | email, complaint | complaint grievance-officer@amazon.in | OK |
| f-03 | Nykaa | Nykaa | call, email, complaint | call 1800-267-88888; email support@nykaa.com; complaint grievanceofficercs@nykaa.com | OK |
| f-04 | (none) | (none) | - | - | OK: no company, so the AI asks a question and no contact is used |
| f-05 | (none) | (none) | - | - | OK: no company, so the AI asks a question and no contact is used |
