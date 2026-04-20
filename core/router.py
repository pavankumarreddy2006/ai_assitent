import { logger } from "../lib/logger";
import { classifyIntent, detectLanguage, extractCity, stripWakePhrase } from "./intent";
import { queryAI, COLLEGE_SYSTEM_PROMPT, TELUGU_SYSTEM_PROMPT } from "./llm_service";
import { getCollegeAnswer, getCollegeContext } from "./college_service";
import { getWeather } from "./weather_service";
import { fetchNews } from "./news_service";
import { searchDuckDuckGo, formatSearchResults } from "./search_service";
import { IMAGE_PATHS, VIDEO_PATH } from "./media_data";
from services.college_service import get_college_answer, get_college_context
# ... remaining imports
const MEDIA_DEFAULTS = {
  show_images: false,
  images: [] as string[],
  show_video: false,
  video_url: null as string | null,
};

interface ChatResponse {
  reply: string;
  intent: string;
  source: string;
  language: string;
  show_images: boolean;
  images: string[];
  show_video: boolean;
  video_url: string | null;
}

export async function routeMessage(
  message: string,
  history: Array<{ role: string; content: string }> = []
): Promise<ChatResponse> {
  const clean = stripWakePhrase(message.trim());

  if (!clean) {
    return {
      reply: "Please say or type a message.",
      intent: "general",
      source: "System",
      language: "en",
      ...MEDIA_DEFAULTS,
    };
  }

  const lang = detectLanguage(clean);
  const intent = classifyIntent(clean);

  logger.info({ intent, lang, message: clean }, "Routing message");

  try {
    if (intent === "images_intent") {
      return {
        reply: lang === "te" ? "ఇప్పుడు క్యాంపస్ చిత్రాలు చూపిస్తున్నాను." : "Here are the campus images for you.",
        intent: "images",
        source: "Media Service",
        language: lang,
        show_images: true,
        images: IMAGE_PATHS,
        show_video: false,
        video_url: null,
      };
    }

    if (intent === "video_intent") {
      return {
        reply: lang === "te" ? "కాలేజీ వీడియో ప్లే చేస్తున్నాను." : "Playing the college promotional video for you.",
        intent: "video",
        source: "Media Service",
        language: lang,
        show_images: false,
        images: [],
        show_video: true,
        video_url: VIDEO_PATH,
      };
    }

    if (intent === "college") {
      return await handleCollege(clean, history, lang);
    }

    if (intent === "weather") {
      return await handleWeather(clean, lang);
    }

    if (intent === "news") {
      return await handleNews(lang);
    }

    if (intent === "search") {
      return await handleSearch(clean, history, lang);
    }

    return await handleGeneral(clean, history, lang);
  } catch (err) {
    logger.error({ err }, "Router error");
    const msg = lang === "te"
      ? "క్షమించండి, ఏదో సమస్య వచ్చింది. దయచేసి మళ్లీ ప్రయత్నించండి."
      : "Something went wrong. Please try again.";
    return {
      reply: msg,
      intent: "general",
      source: "Error",
      language: lang,
      ...MEDIA_DEFAULTS,
    };
  }
}

async function handleCollege(
  message: string,
  history: Array<{ role: string; content: string }>,
  lang: string
): Promise<ChatResponse> {
  const localAnswer = getCollegeAnswer(message, lang);
  if (localAnswer) {
    return {
      reply: localAnswer,
      intent: "college",
      source: "College Database",
      language: lang,
      ...MEDIA_DEFAULTS,
    };
  }

  const context = getCollegeContext();
  const systemPrompt = (lang === "te" ? TELUGU_SYSTEM_PROMPT : COLLEGE_SYSTEM_PROMPT) +
    `\n\nCOLLEGE INFORMATION:\n${context}`;

  const reply = await queryAI(message, history, systemPrompt, lang);
  return {
    reply,
    intent: "college",
    source: "Groq AI + College Database",
    language: lang,
    ...MEDIA_DEFAULTS,
  };
}

async function handleWeather(message: string, lang: string): Promise<ChatResponse> {
  const city = extractCity(message) ?? "Kakinada";
  const weatherData = await getWeather(city, lang);

  let reply: string;
  if (weatherData) {
    if (lang === "te") {
      reply = `${weatherData.city}లో వాతావరణం: ${weatherData.description}, ఉష్ణోగ్రత: ${weatherData.temperature}°C, తేమ: ${weatherData.humidity}%, గాలి వేగం: ${weatherData.wind_speed} km/h.`;
    } else {
      reply = `Weather in ${weatherData.city}: ${weatherData.description}, Temperature: ${weatherData.temperature}°C, Humidity: ${weatherData.humidity}%, Wind: ${weatherData.wind_speed} km/h.`;
    }
  } else {
    reply = lang === "te"
      ? `'${city}' వాతావరణ సమాచారం దొరకలేదు. నగరం పేరు తనిఖీ చేయండి.`
      : `Couldn't find weather data for '${city}'. Please check the city name.`;
  }

  return {
    reply,
    intent: "weather",
    source: "Open-Meteo Weather API",
    language: lang,
    ...MEDIA_DEFAULTS,
  };
}

async function handleNews(lang: string): Promise<ChatResponse> {
  const articles = await fetchNews("India education college news");

  let reply: string;
  if (articles.length > 0) {
    const header = lang === "te" ? "తాజా వార్తలు:\n" : "Here are the latest headlines:\n";
    const lines = articles.slice(0, 5).map((a, i) => `${i + 1}. ${a.title} — ${a.source}`);
    reply = header + lines.join("\n");
  } else {
    reply = lang === "te"
      ? "ప్రస్తుతం వార్తలు తీసుకోలేకపోయాము. తర్వాత మళ్ళీ ప్రయత్నించండి."
      : "Couldn't fetch the latest news right now. Please try again later.";
  }

  return {
    reply,
    intent: "news",
    source: "News API",
    language: lang,
    ...MEDIA_DEFAULTS,
  };
}

async function handleSearch(
  message: string,
  history: Array<{ role: string; content: string }>,
  lang: string
): Promise<ChatResponse> {
  const results = await searchDuckDuckGo(message);
  const searchContext = formatSearchResults(results);

  const prompt = results.length > 0
    ? `Based on this search info, answer the question: "${message}"\n\nSearch results:\n${searchContext}\n\nProvide a clear, direct answer.`
    : message;

  const reply = await queryAI(prompt, history, undefined, lang);
  return {
    reply,
    intent: "search",
    source: results.length > 0 ? "Live Web + Groq AI" : "Groq AI",
    language: lang,
    ...MEDIA_DEFAULTS,
  };
}

async function handleGeneral(
  message: string,
  history: Array<{ role: string; content: string }>,
  lang: string
): Promise<ChatResponse> {
  const reply = await queryAI(message, history, undefined, lang);
  return {
    reply,
    intent: "general",
    source: "Groq AI",
    language: lang,
    ...MEDIA_DEFAULTS,
  };
}
