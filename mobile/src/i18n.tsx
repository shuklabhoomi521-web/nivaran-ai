import React, { createContext, useContext } from 'react';

export type Lang = 'en' | 'hi' | 'ta';
export const LANGS: { code: Lang; label: string }[] = [{ code: 'en', label: 'English' }, { code: 'hi', label: 'हिन्दी' }, { code: 'ta', label: 'தமிழ்' }];

// First draft of the Hindi and Tamil text: it has NOT been checked by a native speaker yet (see docs/notes/mobile-i18n.md).
export const STRINGS = {
  en: {
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
