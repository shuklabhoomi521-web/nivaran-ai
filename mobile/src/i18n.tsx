import React, { createContext, useContext } from 'react';

export type Lang = 'en' | 'hi' | 'ta';
export const LANGS: { code: Lang; label: string }[] = [{ code: 'en', label: 'English' }, { code: 'hi', label: 'हिन्दी' }, { code: 'ta', label: 'தமிழ்' }];

// First draft of the Hindi and Tamil text: it has NOT been checked by a native speaker yet (see docs/notes/mobile-i18n.md).
export const STRINGS = {
  en: {
    'kpi.open': 'Open complaints', 'kpi.attention': 'Need your attention', 'kpi.escalated': 'Escalated', 'kpi.resolved': 'Resolved',
    'state.new': 'Not sent yet', 'state.waiting': 'Waiting for a reply', 'state.escalated': 'Escalated', 'state.resolved': 'Solved', 'state.closed': 'Closed',
    'rung.first_contact': 'First message', 'rung.follow_up': 'Follow-up', 'rung.grievance_officer': 'Grievance officer', 'rung.appellate': 'Appellate authority', 'rung.regulator': "Regulator's portal",
    'fu.checking': 'Checking the schedule…', 'fu.solved': 'Solved', 'fu.closed': 'Stopped by you', 'fu.none': 'No follow-up planned',
    'fu.approve': 'Waiting for your approval to send: {what}', 'fu.overdue': 'Follow-up overdue since {date}: {what}', 'fu.next': 'Next follow-up on {date}: {what}', 'fu.started': 'started {date}',
    'nav.home': 'Home', 'nav.home.hint': 'Your dashboard', 'nav.chat': 'Tell our AI in chat', 'nav.chat.hint': 'Type or speak your problem', 'nav.call': 'Tell our AI on a call', 'nav.call.hint': 'Talk to it by voice',
    'nav.complaints': 'My complaints', 'nav.complaints.hint': 'Ongoing and resolved', 'nav.profile': 'My profile', 'nav.profile.hint': 'Your details and numbers', 'nav.menu': 'Menu',
    'home.recent': 'Your recent complaints', 'home.none': 'Nothing yet. When you tell our AI about a problem, you can follow it here.', 'home.glad': 'Glad to help',
    'greet.morning': 'Good morning', 'greet.afternoon': 'Good afternoon', 'greet.evening': 'Good evening', 'greet.night': 'Hello',
    'cmp.title': 'My complaints', 'cmp.ongoing': 'Ongoing', 'cmp.resolved': 'Resolved',
    'prof.title': 'My profile', 'prof.numbers': 'My complaints in numbers', 'prof.total': 'Total', 'prof.ongoing': 'Ongoing', 'prof.resolved': 'Resolved', 'prof.escalated': 'Escalated', 'prof.stopped': 'Stopped by me', 'prof.details': 'My details', 'prof.edit': 'Edit my details', 'prof.signout': 'Sign out',
    'common.back': 'Back',
    'cases.title': 'My cases', 'cases.new': 'New case', 'cases.empty': 'No cases yet. Tap "New case" and tell us the problem once, in your own words.',
    'new.title': 'New case', 'new.intro': 'Tell us the problem once, in your own words and your own language.', 'new.understand': 'Understand my problem',
    'new.speak': 'Speak instead of typing', 'new.stop': 'Stop and write it down', 'new.right': 'Is this right?', 'new.privacy': 'Privacy',
    'new.agree': 'I have read this and agree.', 'new.adult': 'I am 18 years old or older.', 'new.create': 'Create case', 'new.change': 'Change my text',
    'case.steps': 'Steps', 'case.next': 'Next', 'case.timeline': 'Timeline', 'case.write': 'Write the letter', 'case.approve': 'Approve', 'case.send': 'Send this email',
    'case.replies': 'Check my inbox for replies', 'case.solved': 'It is solved', 'case.stop': 'Stop this case', 'case.delete': 'Delete my data for this case',
    'case.call': 'Call for me (practice)', 'case.kit': 'Open the filing kit', 'case.did': 'I did this step myself',
  },
  hi: {
    'kpi.open': 'खुली शिकायतें', 'kpi.attention': 'आपके ध्यान की ज़रूरत', 'kpi.escalated': 'आगे बढ़ाई गईं', 'kpi.resolved': 'हल हुईं',
    'state.new': 'अभी भेजी नहीं', 'state.waiting': 'जवाब का इंतज़ार', 'state.escalated': 'आगे बढ़ाई गई', 'state.resolved': 'हल हुई', 'state.closed': 'बंद',
    'rung.first_contact': 'पहला संदेश', 'rung.follow_up': 'फ़ॉलो-अप', 'rung.grievance_officer': 'शिकायत अधिकारी', 'rung.appellate': 'अपीलीय प्राधिकारी', 'rung.regulator': 'नियामक का पोर्टल',
    'fu.checking': 'समय-सारणी देख रहे हैं…', 'fu.solved': 'हल हुई', 'fu.closed': 'आपने रोक दी', 'fu.none': 'कोई फ़ॉलो-अप तय नहीं',
    'fu.approve': 'भेजने के लिए आपकी मंज़ूरी का इंतज़ार: {what}', 'fu.overdue': '{date} से फ़ॉलो-अप बाकी: {what}', 'fu.next': 'अगला फ़ॉलो-अप {date} को: {what}', 'fu.started': '{date} को शुरू हुई',
    'nav.home': 'होम', 'nav.home.hint': 'आपका डैशबोर्ड', 'nav.chat': 'चैट में AI को बताएँ', 'nav.chat.hint': 'लिखकर या बोलकर समस्या बताएँ', 'nav.call': 'कॉल पर AI को बताएँ', 'nav.call.hint': 'आवाज़ में बात करें',
    'nav.complaints': 'मेरी शिकायतें', 'nav.complaints.hint': 'चल रही और हल हुई', 'nav.profile': 'मेरी प्रोफ़ाइल', 'nav.profile.hint': 'आपकी जानकारी और आँकड़े', 'nav.menu': 'मेनू',
    'home.recent': 'आपकी हाल की शिकायतें', 'home.none': 'अभी कुछ नहीं। जब आप AI को समस्या बताएँगे, तो उसे यहाँ देख सकेंगे।', 'home.glad': 'मदद करके खुशी हुई',
    'greet.morning': 'सुप्रभात', 'greet.afternoon': 'नमस्कार', 'greet.evening': 'शुभ संध्या', 'greet.night': 'नमस्ते',
    'cmp.title': 'मेरी शिकायतें', 'cmp.ongoing': 'चल रही', 'cmp.resolved': 'हल हुई',
    'prof.title': 'मेरी प्रोफ़ाइल', 'prof.numbers': 'मेरी शिकायतें आँकड़ों में', 'prof.total': 'कुल', 'prof.ongoing': 'चल रही', 'prof.resolved': 'हल हुई', 'prof.escalated': 'आगे बढ़ाई गई', 'prof.stopped': 'मैंने रोकी', 'prof.details': 'मेरी जानकारी', 'prof.edit': 'जानकारी बदलें', 'prof.signout': 'साइन आउट',
    'common.back': 'वापस',
    'cases.title': 'मेरी शिकायतें', 'cases.new': 'नई शिकायत', 'cases.empty': 'अभी कोई शिकायत नहीं है। "नई शिकायत" दबाएँ और अपनी भाषा में समस्या एक बार बताइए।',
    'new.title': 'नई शिकायत', 'new.intro': 'अपनी समस्या अपनी भाषा में, अपने शब्दों में, बस एक बार बताइए।', 'new.understand': 'मेरी समस्या समझें',
    'new.speak': 'टाइप करने की जगह बोलकर बताएँ', 'new.stop': 'रोकें और लिखें', 'new.right': 'क्या यह सही है?', 'new.privacy': 'गोपनीयता',
    'new.agree': 'मैंने इसे पढ़ लिया है और मैं सहमत हूँ।', 'new.adult': 'मेरी उम्र 18 साल या उससे अधिक है।', 'new.create': 'शिकायत बनाएँ', 'new.change': 'मेरा लिखा बदलें',
    'case.steps': 'चरण', 'case.next': 'अगला कदम', 'case.timeline': 'अब तक क्या हुआ', 'case.write': 'पत्र लिखें', 'case.approve': 'मंज़ूर करें', 'case.send': 'यह ईमेल भेजें',
    'case.replies': 'जवाब के लिए मेरा इनबॉक्स देखें', 'case.solved': 'समस्या हल हो गई', 'case.stop': 'यह शिकायत बंद करें', 'case.delete': 'इस शिकायत का मेरा डेटा मिटाएँ',
    'case.call': 'मेरी तरफ़ से कॉल करें (अभ्यास)', 'case.kit': 'शिकायत दर्ज करने की किट खोलें', 'case.did': 'यह कदम मैंने खुद किया',
  },
  ta: {
    'kpi.open': 'திறந்த புகார்கள்', 'kpi.attention': 'உங்கள் கவனம் தேவை', 'kpi.escalated': 'மேலே எடுத்துச்சென்றவை', 'kpi.resolved': 'தீர்ந்தவை',
    'state.new': 'இன்னும் அனுப்பவில்லை', 'state.waiting': 'பதிலுக்காகக் காத்திருப்பு', 'state.escalated': 'மேலே எடுத்துச்செல்லப்பட்டது', 'state.resolved': 'தீர்ந்தது', 'state.closed': 'மூடப்பட்டது',
    'rung.first_contact': 'முதல் செய்தி', 'rung.follow_up': 'பின்தொடர்தல்', 'rung.grievance_officer': 'குறைதீர் அலுவலர்', 'rung.appellate': 'மேல்முறையீட்டு அதிகாரி', 'rung.regulator': 'ஒழுங்குமுறை ஆணையத்தின் தளம்',
    'fu.checking': 'அட்டவணையைப் பார்க்கிறோம்…', 'fu.solved': 'தீர்ந்தது', 'fu.closed': 'நீங்கள் நிறுத்தினீர்கள்', 'fu.none': 'பின்தொடர்தல் திட்டமிடப்படவில்லை',
    'fu.approve': 'அனுப்ப உங்கள் ஒப்புதலுக்காகக் காத்திருப்பு: {what}', 'fu.overdue': '{date} முதல் பின்தொடர்தல் தாமதம்: {what}', 'fu.next': 'அடுத்த பின்தொடர்தல் {date}: {what}', 'fu.started': '{date} அன்று தொடங்கியது',
    'nav.home': 'முகப்பு', 'nav.home.hint': 'உங்கள் டாஷ்போர்டு', 'nav.chat': 'அரட்டையில் AI-யிடம் சொல்லுங்கள்', 'nav.chat.hint': 'எழுதி அல்லது பேசிச் சொல்லுங்கள்', 'nav.call': 'அழைப்பில் AI-யிடம் சொல்லுங்கள்', 'nav.call.hint': 'குரலில் பேசுங்கள்',
    'nav.complaints': 'என் புகார்கள்', 'nav.complaints.hint': 'நடப்பவை மற்றும் தீர்ந்தவை', 'nav.profile': 'என் சுயவிவரம்', 'nav.profile.hint': 'உங்கள் விவரங்களும் எண்களும்', 'nav.menu': 'மெனு',
    'home.recent': 'உங்கள் சமீபத்திய புகார்கள்', 'home.none': 'இன்னும் எதுவும் இல்லை. AI-யிடம் பிரச்சினையைச் சொன்னால் இங்கே பின்தொடரலாம்.', 'home.glad': 'உதவ மகிழ்ச்சி',
    'greet.morning': 'காலை வணக்கம்', 'greet.afternoon': 'மதிய வணக்கம்', 'greet.evening': 'மாலை வணக்கம்', 'greet.night': 'வணக்கம்',
    'cmp.title': 'என் புகார்கள்', 'cmp.ongoing': 'நடப்பவை', 'cmp.resolved': 'தீர்ந்தவை',
    'prof.title': 'என் சுயவிவரம்', 'prof.numbers': 'என் புகார்கள் எண்களில்', 'prof.total': 'மொத்தம்', 'prof.ongoing': 'நடப்பவை', 'prof.resolved': 'தீர்ந்தவை', 'prof.escalated': 'மேலே எடுத்துச்சென்றவை', 'prof.stopped': 'நான் நிறுத்தியவை', 'prof.details': 'என் விவரங்கள்', 'prof.edit': 'விவரங்களை மாற்று', 'prof.signout': 'வெளியேறு',
    'common.back': 'பின்',
    'cases.title': 'என் புகார்கள்', 'cases.new': 'புதிய புகார்', 'cases.empty': 'இன்னும் புகார் இல்லை. "புதிய புகார்" என்பதைத் தொட்டு, உங்கள் மொழியில் பிரச்சினையை ஒருமுறை சொல்லுங்கள்.',
    'new.title': 'புதிய புகார்', 'new.intro': 'உங்கள் பிரச்சினையை உங்கள் மொழியில், உங்கள் வார்த்தைகளில் ஒருமுறை சொல்லுங்கள்.', 'new.understand': 'என் பிரச்சினையைப் புரிந்துகொள்',
    'new.speak': 'தட்டச்சுக்கு பதிலாக பேசுங்கள்', 'new.stop': 'நிறுத்தி எழுது', 'new.right': 'இது சரியா?', 'new.privacy': 'தனியுரிமை',
    'new.agree': 'இதைப் படித்தேன், ஒப்புக்கொள்கிறேன்.', 'new.adult': 'எனக்கு 18 வயது அல்லது அதற்கு மேல்.', 'new.create': 'புகாரை உருவாக்கு', 'new.change': 'என் எழுத்தை மாற்று',
    'case.steps': 'படிகள்', 'case.next': 'அடுத்த படி', 'case.timeline': 'இதுவரை நடந்தவை', 'case.write': 'கடிதம் எழுது', 'case.approve': 'அங்கீகரி', 'case.send': 'இந்த மின்னஞ்சலை அனுப்பு',
    'case.replies': 'பதில்களுக்காக என் இன்பாக்ஸைப் பார்', 'case.solved': 'பிரச்சினை தீர்ந்தது', 'case.stop': 'இந்தப் புகாரை நிறுத்து', 'case.delete': 'இந்தப் புகாரின் என் தரவை அழி',
    'case.call': 'எனக்காக அழை (பயிற்சி)', 'case.kit': 'புகார் தாக்கல் கிட்டைத் திற', 'case.did': 'இந்தப் படியை நானே செய்தேன்',
  },
} as const;

export type Key = keyof typeof STRINGS.en;

export function translate(lang: Lang, key: Key): string {
  return (STRINGS[lang] as Record<string, string>)[key] ?? STRINGS.en[key];
}

const Ctx = createContext<{ lang: Lang; setLang: (l: Lang) => void }>({ lang: 'en', setLang: () => undefined });
export const LangProvider = Ctx.Provider;
export function useLang() { return useContext(Ctx); }
export function useT() { const { lang } = useContext(Ctx); return (key: Key) => translate(lang, key); }
export function fill(text: string, vars: Record<string, string>): string { return text.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? ''); }
