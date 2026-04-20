import { logger } from "../lib/logger";

const GNEWS_API = process.env.GNEWS_API;
const NEWS_API_KEY = process.env.NEWS_API_KEY;
const NEWS_DATA_API = process.env.NEWS_DATA_API;

interface Article {
  title: string;
  description?: string;
  url: string;
  source: string;
  published_at: string;
}

async function fetchGNews(query: string): Promise<Article[]> {
  if (!GNEWS_API) return [];
  const resp = await fetch(
    `https://gnews.io/api/v4/search?q=${encodeURIComponent(query)}&lang=en&max=10&apikey=${GNEWS_API}`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!resp.ok) return [];
  const data = await resp.json() as { articles?: Array<{ title: string; description: string; url: string; source: { name: string }; publishedAt: string }> };
  return (data.articles || []).map(a => ({
    title: a.title,
    description: a.description,
    url: a.url,
    source: a.source?.name ?? "Unknown",
    published_at: a.publishedAt,
  }));
}

async function fetchNewsData(query: string): Promise<Article[]> {
  if (!NEWS_DATA_API) return [];
  const resp = await fetch(
    `https://newsdata.io/api/1/news?q=${encodeURIComponent(query)}&language=en&apikey=${NEWS_DATA_API}`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!resp.ok) return [];
  const data = await resp.json() as { results?: Array<{ title: string; description: string; link: string; source_id: string; pubDate: string }> };
  return (data.results || []).slice(0, 10).filter(a => a.title).map(a => ({
    title: a.title,
    description: a.description,
    url: a.link,
    source: a.source_id ?? "Unknown",
    published_at: a.pubDate,
  }));
}

async function fetchNewsApi(query: string): Promise<Article[]> {
  if (!NEWS_API_KEY) return [];
  const resp = await fetch(
    `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&sortBy=publishedAt&pageSize=10&apiKey=${NEWS_API_KEY}`,
    { signal: AbortSignal.timeout(10000) }
  );
  if (!resp.ok) return [];
  const data = await resp.json() as { articles?: Array<{ title: string; description: string; url: string; source: { name: string }; publishedAt: string }> };
  return (data.articles || []).map(a => ({
    title: a.title,
    description: a.description,
    url: a.url,
    source: a.source?.name ?? "Unknown",
    published_at: a.publishedAt,
  }));
}

export async function fetchNews(query?: string): Promise<Article[]> {
  const searchQuery = query || "latest India education news";

  const providers = [
    { name: "gnews", fn: () => fetchGNews(searchQuery), enabled: !!GNEWS_API },
    { name: "newsdata", fn: () => fetchNewsData(searchQuery), enabled: !!NEWS_DATA_API },
    { name: "newsapi", fn: () => fetchNewsApi(searchQuery), enabled: !!NEWS_API_KEY },
  ];

  for (const { name, fn, enabled } of providers) {
    if (!enabled) continue;
    try {
      const articles = await fn();
      if (articles.length > 0) {
        logger.info({ provider: name }, "News fetched");
        return articles;
      }
    } catch (err) {
      logger.warn({ err, provider: name }, "News provider failed");
    }
  }

  return [];
}
