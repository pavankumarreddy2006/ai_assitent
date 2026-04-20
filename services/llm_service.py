import { logger } from "../lib/logger";

const AI_BASE_URL = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL;
const AI_API_KEY = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const OPEN_ROUTER_API = process.env.OPEN_ROUTER_API;
const GROQ_MODEL = "llama3-8b-8192";
const OPENROUTER_MODEL = "openai/gpt-3.5-turbo";
const REPLIT_MODEL = "gpt-5-mini";

export const COLLEGE_SYSTEM_PROMPT = `You are the official AI assistant for Ideal College of Arts and Sciences,
located at Vidyuth Nagar, Kakinada, Andhra Pradesh.

LANGUAGE RULE (VERY IMPORTANT):
- If the user writes in Telugu → reply ONLY in Telugu.
- If the user writes in English → reply ONLY in English.
- If the user writes Roman Telugu → reply in Telugu.
- Never switch languages unless the user switches first.

BEHAVIOR:
- Be friendly, helpful, and professional.
- For college questions, give direct and accurate answers.
- For general questions, be concise and informative.
- Always greet warmly if it is the first message.
- Keep answers clear and easy to understand.

COLLEGE CONTACT (use when needed):
- Phone: 0884-2384382 / 0884-2384381
- Email: idealcolleges@gmail.com
- Website: https://idealcollege.edu.in
- Location: Vidyuth Nagar, Kakinada, Andhra Pradesh`;

export const TELUGU_SYSTEM_PROMPT = `మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.

భాషా నియమం: వినియోగదారు తెలుగులో మాట్లాడితే తెలుగులోనే సమాధానం ఇవ్వండి.

ప్రవర్తన:
- స్నేహపూర్వకంగా మరియు సహాయకరంగా ఉండండి.
- కాలేజీ సమాచారాన్ని స్పష్టంగా ఇవ్వండి.
- సమాధానాలు సంక్షిప్తంగా ఉండాలి.

కాలేజీ సంప్రదింపు:
- ఫోన్: 0884-2384382 / 0884-2384381
- ఇమెయిల్: idealcolleges@gmail.com
- వెబ్‌సైట్: https://idealcollege.edu.in
- చిరునామా: విద్యుత్ నగర్, కాకినాడ, ఆంధ్రప్రదేశ్`;

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

function buildMessages(
  prompt: string,
  history: Array<{ role: string; content: string }> = [],
  systemPrompt?: string,
  lang = "en"
): ChatMessage[] {
  const sys = systemPrompt ?? (lang === "te" ? TELUGU_SYSTEM_PROMPT : COLLEGE_SYSTEM_PROMPT);
  const messages: ChatMessage[] = [{ role: "system", content: sys }];

  for (const msg of history.slice(-10)) {
    if ((msg.role === "user" || msg.role === "assistant") && msg.content?.trim()) {
      messages.push({ role: msg.role as "user" | "assistant", content: msg.content.trim() });
    }
  }

  messages.push({ role: "user", content: prompt });
  return messages;
}

async function callOpenAICompatible(
  baseUrl: string,
  apiKey: string,
  model: string,
  messages: ChatMessage[],
  opts: { useCompletionTokens?: boolean; skipTemperature?: boolean } = {}
): Promise<string> {
  const body: Record<string, unknown> = { model, messages };
  if (opts.useCompletionTokens) {
    body.max_completion_tokens = 1200;
  } else {
    body.max_tokens = 1200;
  }
  if (!opts.skipTemperature) {
    body.temperature = 0.7;
  }

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30000),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  const data = await response.json() as { choices: Array<{ message: { content: string } }> };
  return data.choices[0].message.content;
}

async function queryReplitAI(
  prompt: string,
  history: Array<{ role: string; content: string }> = [],
  systemPrompt?: string,
  lang = "en"
): Promise<string> {
  if (!AI_BASE_URL || !AI_API_KEY) throw new Error("Replit AI integration not configured");
  const messages = buildMessages(prompt, history, systemPrompt, lang);
  return callOpenAICompatible(AI_BASE_URL, AI_API_KEY, REPLIT_MODEL, messages, { useCompletionTokens: true, skipTemperature: true });
}

async function queryGroq(
  prompt: string,
  history: Array<{ role: string; content: string }> = [],
  systemPrompt?: string,
  lang = "en"
): Promise<string> {
  if (!GROQ_API_KEY) throw new Error("GROQ_API_KEY not configured");
  const messages = buildMessages(prompt, history, systemPrompt, lang);
  return callOpenAICompatible("https://api.groq.com/openai/v1", GROQ_API_KEY, GROQ_MODEL, messages, {});
}

async function queryOpenRouter(
  prompt: string,
  history: Array<{ role: string; content: string }> = [],
  systemPrompt?: string,
  lang = "en"
): Promise<string> {
  if (!OPEN_ROUTER_API) throw new Error("OPEN_ROUTER_API not configured");
  const messages = buildMessages(prompt, history, systemPrompt, lang);
  return callOpenAICompatible("https://openrouter.ai/api/v1", OPEN_ROUTER_API, OPENROUTER_MODEL, messages, {});
}

export async function queryAI(
  prompt: string,
  history: Array<{ role: string; content: string }> = [],
  systemPrompt?: string,
  lang = "en"
): Promise<string> {
  // Try Replit AI first (always available), then Groq, then OpenRouter as fallbacks
  if (AI_BASE_URL && AI_API_KEY) {
    try {
      return await queryReplitAI(prompt, history, systemPrompt, lang);
    } catch (err) {
      logger.warn({ err }, "Replit AI failed, trying Groq");
    }
  }

  if (GROQ_API_KEY) {
    try {
      return await queryGroq(prompt, history, systemPrompt, lang);
    } catch (err) {
      logger.warn({ err }, "Groq failed, trying OpenRouter");
    }
  }

  if (OPEN_ROUTER_API) {
    try {
      return await queryOpenRouter(prompt, history, systemPrompt, lang);
    } catch (err) {
      logger.error({ err }, "All AI providers failed");
      throw err;
    }
  }

  throw new Error("No AI providers configured");
}
