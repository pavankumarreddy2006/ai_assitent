import { COLLEGE_KEYWORDS } from "./college_data";

const IMAGE_INTENT_PHRASES = [
  "college photos", "college images", "college pictures", "college gallery",
  "campus photos", "campus images", "campus pictures", "campus gallery",
  "show college photos", "show campus photos", "show photos", "show images",
  "campus tour", "virtual tour",
  "ఫోటోలు చూపించు", "చిత్రాలు చూపించు", "క్యాంపస్ ఫోటో", "కాలేజీ ఫోటో",
];

const VIDEO_INTENT_PHRASES = [
  "college video", "campus video", "promotional video", "promo video",
  "play college video", "show college video", "watch college video",
  "play video", "show video", "watch video", "full details", "explain college",
  "కాలేజీ వీడియో", "క్యాంపస్ వీడియో", "వీడియో ప్లే", "వీడియో చూపించు",
];

const WAKE_PHRASES = [
  "hello ideal college ai", "hello ideal ai", "hi ideal college ai",
  "ideal college ai", "hello jarvis", "hi jarvis", "jarvis",
  "హలో ఐడియల్ కాలేజ్ ఏఐ", "ఐడియల్ కాలేజ్ ఏఐ",
];

const ROMAN_TELUGU_WORDS = new Set([
  "nenu", "meeru", "nuvvu", "adigina", "adigithe", "matladithe", "matladu",
  "matladutunnanu", "telugu", "cheppu", "chepandi", "cheppandi", "ivvu",
  "ivvandi", "enti", "emiti", "ela", "enduku", "ekkada", "evaru",
  "undi", "unnayi", "kavali", "chesi", "cheyyi", "cheyyandi", "theliyali",
  "gurunchi", "varthalu", "vartalu", "tajaga", "vathavaranam", "vaatavaranam",
  "varsham", "courseulu", "chupinchu", "aadinchu",
]);

const WEATHER_KEYWORDS = [
  "weather", "temperature", "rain", "sunny", "cloudy", "forecast",
  "humidity", "wind", "climate", "hot", "cold", "storm",
];

const NEWS_KEYWORDS = [
  "news", "headlines", "latest", "breaking", "current affairs",
  "trending", "update", "report", "today's news",
];

const SEARCH_KEYWORDS = [
  "search", "find", "look up", "what is", "who is", "where is",
  "how to", "define", "meaning of", "explain", "tell me about",
  "information about", "details about",
];

const COLLEGE_HINTS_EN = new Set([
  "admission", "admissions", "course", "courses", "fee", "fees",
  "principal", "hostel", "library", "placement", "placements",
  "college", "campus", "timings", "contact", "scholarship",
]);

const _SCOPE = ["college", "campus", "ideal", "jarvis", "కాలేజీ", "క్యాంపస్", "ఐడియల్"];
const _MEDIA_PIC = ["photo", "photos", "image", "images", "picture", "pictures", "gallery", "ఫోటో", "చిత్ర"];
const _MEDIA_VID = ["video", "play", "watch", "వీడియో"];

function imagesIntentFromText(msg: string): boolean {
  return IMAGE_INTENT_PHRASES.some(p => msg.includes(p)) ||
    (_SCOPE.some(s => msg.includes(s)) && _MEDIA_PIC.some(m => msg.includes(m)));
}

function videoIntentFromText(msg: string): boolean {
  return VIDEO_INTENT_PHRASES.some(p => msg.includes(p)) ||
    (_SCOPE.some(s => msg.includes(s)) && _MEDIA_VID.some(v => msg.includes(v)));
}

function normalizeText(text: string): string {
  return (text || "").trim().toLowerCase().replace(/\s+/g, " ");
}

export function stripWakePhrase(text: string): string {
  const normalized = normalizeText(text);
  for (const phrase of WAKE_PHRASES.sort((a, b) => b.length - a.length)) {
    if (normalized.startsWith(phrase)) {
      return normalized.slice(phrase.length).replace(/^[\s,.:;-]+/, "");
    }
  }
  return normalized;
}

export function detectLanguage(text: string): string {
  const teluguChars = Array.from(text).filter(ch => ch >= "\u0C00" && ch <= "\u0C7F").length;
  const totalChars = Math.max(text.replace(/\s/g, "").length, 1);
  if (teluguChars / totalChars > 0.15) return "te";

  const words = (text.toLowerCase().match(/[a-zA-Z]+/g) || []);
  if (!words.length) return "en";

  const romanHits = words.filter(w => ROMAN_TELUGU_WORDS.has(w)).length;
  if (romanHits >= 2) return "te";
  return "en";
}

export function classifyIntent(message: string): string {
  const msg = normalizeText(message);
  const msgWords = new Set((msg.match(/[a-zA-Z]+/g) || []));

  if (videoIntentFromText(msg)) return "video_intent";
  if (imagesIntentFromText(msg)) return "images_intent";

  for (const hint of COLLEGE_HINTS_EN) {
    if (msgWords.has(hint)) return "college";
  }
  if (COLLEGE_KEYWORDS.some(kw => msg.includes(kw.toLowerCase()))) return "college";
  if (WEATHER_KEYWORDS.some(kw => msg.includes(kw))) return "weather";
  if (NEWS_KEYWORDS.some(kw => msg.includes(kw))) return "news";
  if (SEARCH_KEYWORDS.some(kw => msg.includes(kw))) return "search";
  if (msg.includes("?")) return "search";
  return "general";
}

export function extractCity(message: string): string | null {
  const patterns = [
    /weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)(?:\?|$|\.)/i,
    /weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})/i,
    /temperature\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})/i,
    /how(?:'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z][a-zA-Z\s]{1,30})/i,
    /climate\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})/i,
  ];

  for (const pattern of patterns) {
    const match = message.match(pattern);
    if (match) {
      const city = match[1].replace(/[?.,!]+$/, "").trim();
      if (city && city.length >= 2 && city.length <= 30) return city;
    }
  }

  for (const word of message.split(/\s+/)) {
    const cleaned = word.replace(/[^a-zA-Z]/g, "");
    if (cleaned.length >= 3 && cleaned[0] === cleaned[0].toUpperCase()) {
      const lower = cleaned.toLowerCase();
      const skip = new Set(["weather", "what", "how", "tell", "the", "for", "now", "today", "check", "please", "show", "give", "temperature", "forecast", "update", "current"]);
      if (!skip.has(lower)) return cleaned;
    }
  }
  return null;
}
