# Second check of the directory (by Claude, 15 Oct 2026)

This is an independent AI check of the 26 sources that were "read in a browser"
(not machine-checked), plus a look at the needs_check gaps. It is NOT a human check.
Method: fetched each official page again and asked whether the exact number/email is there.

## Confirmed on the official page (12 of 26)
- IndiGo (goindigo.in/contact-us.html): 0124-4973838, 0124-6173838,
  customer.experience@goindigo.in, nodalofficer@goindigo.in, appellateauthority@goindigo.in. All present.
- Air India (grievance-resolution page): nodalofficer@airindia.com, appellateauthority@airindia.com. Present.
- Meesho (legal/privacy): legalsupport@meesho.com, Grievance Officer "Murthy S.N". Present.
- Nykaa (policy): grievanceofficercs@nykaa.com and support@nykaa.com. Present.
- Star Health (contact + grievance-redressal): all 5 numbers and support@starhealth.in present.
- ICICI Lombard (customer-support): 1800 2666 and customersupport@icicilombard.com. Present.
- Swiggy (swiggy_customer_care): "no official customer care phone line" statement. Present.

## LABEL PROBLEM to fix (Star Health)
On the official page, 1800 425 2255 is labelled "Buy Policy" and 1800 102 4477 is
"Renew Policy". They are sales lines, not complaint lines. For complaints the page lists:
- "Grievance Care - 044 4366 4600"
- "Senior Citizen Grievance - 044 6900 7500"
- "General Helpline - 044 6900 6900"
Fix: relabel the two toll-free numbers, add the two grievance numbers (with exact
quotes from a machine fetch), and make the picker prefer Grievance Care for complaints.

## Could NOT confirm (page needs JavaScript or blocked my fetch) — human check needed
- Swiggy privacy-policy: grievances@swiggy.in, support@swiggy.in
- Uber grievance page: +91 80 4685 2525, +91 891 451 2030, grievanceredressaloffice@uber.com
- Domino's contact: 1800-208-1234, guestcaredominos@jublfood.com
- Zepto customer-support: "no phone line" statement
None of these looked wrong; I simply could not load them.

## needs_check gaps
- Nykaa phone (fills a gap): the official nykaa.com/policy page shows a Customer Service
  Desk number 1800-267-88888 (8 AM - 10 PM, Mon-Sun). Re-fetch it to capture the exact line.
- BSNL: the official grievance page (bsnl.co.in/opencms/bsnl/BSNL/about_us/consumer_griev.html)
  lists cmdcomplaints@bsnl.co.in, ddgpg@bsnl.co.in and 011-23372200. WARNING: this page
  looks old (the related customer-care page lists Dataone/Sancharnet numbers that are
  likely obsolete). Use the emails only with a "may be outdated" warning; do NOT add the
  old Dataone/Sancharnet numbers.
- Ola and Myntra: their official pages blocked my fetch too, and search only returned
  third-party sites (not allowed). These need a human with a real browser
  (Myntra: myntra.com/termsofuse, section "22. Grievance Officer"; Ola: help.olacabs.com).
