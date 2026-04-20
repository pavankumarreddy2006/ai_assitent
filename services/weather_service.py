import { logger } from "../lib/logger";

const WEATHER_API_KEY = process.env.WEATHER_API_KEY;

const WEATHER_CODES: Record<number, string> = {
  0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
  45: "Foggy", 48: "Rime fog",
  51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
  61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
  71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
  80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
  95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
};

const WEATHER_CODES_TE: Record<number, string> = {
  0: "ఆకాశం స్వచ్ఛంగా ఉంది", 1: "ప్రధానంగా స్వచ్ఛంగా", 2: "పాక్షికంగా మేఘావృతం",
  3: "పూర్తిగా మేఘావృతం", 51: "తేలికపాటి జల్లు", 61: "తేలికపాటి వర్షం",
  63: "మితమైన వర్షం", 65: "భారీ వర్షం", 80: "వర్షపు జల్లులు",
  95: "పిడుగుపాటు వర్షం",
};

interface WeatherResult {
  city: string;
  temperature: number;
  description: string;
  humidity: number;
  wind_speed: number;
}

async function getWeatherApi(city: string): Promise<WeatherResult | null> {
  const response = await fetch(
    `https://api.weatherapi.com/v1/current.json?key=${WEATHER_API_KEY}&q=${encodeURIComponent(city)}&aqi=no`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!response.ok) return null;

  const payload = await response.json() as {
    current: { temp_c: number; humidity: number; wind_kph: number; condition: { text: string } };
    location: { name: string };
  };
  const current = payload.current;
  const location = payload.location;

  return {
    city: location.name,
    temperature: current.temp_c,
    description: current.condition.text,
    humidity: current.humidity,
    wind_speed: current.wind_kph,
  };
}

async function getOpenMeteoWeather(city: string, lang: string): Promise<WeatherResult | null> {
  const geoResp = await fetch(
    `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!geoResp.ok) return null;

  const geoData = await geoResp.json() as { results?: Array<{ latitude: number; longitude: number; name: string }> };
  const results = geoData.results;
  if (!results || results.length === 0) return null;

  const { latitude: lat, longitude: lon, name } = results[0];

  const weatherResp = await fetch(
    `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!weatherResp.ok) return null;

  const weatherData = await weatherResp.json() as {
    current: { temperature_2m: number; relative_humidity_2m: number; wind_speed_10m: number; weather_code: number };
  };
  const current = weatherData.current;
  const code = current.weather_code ?? 0;

  return {
    city: name,
    temperature: current.temperature_2m,
    description: lang === "te" ? (WEATHER_CODES_TE[code] ?? "తెలియదు") : (WEATHER_CODES[code] ?? "Unknown"),
    humidity: current.relative_humidity_2m,
    wind_speed: current.wind_speed_10m,
  };
}

export async function getWeather(city: string, lang = "en"): Promise<WeatherResult | null> {
  try {
    if (WEATHER_API_KEY) {
      const result = await getWeatherApi(city);
      if (result) return result;
    }
    return await getOpenMeteoWeather(city, lang);
  } catch (err) {
    logger.warn({ err }, "Weather fetch failed");
    return null;
  }
}
