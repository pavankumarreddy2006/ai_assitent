import { logger } from "../lib/logger";

export async function searchDuckDuckGo(query: string): Promise<Array<{ title: string; snippet: string; url: string }>> {
  try {
    const formData = new URLSearchParams({ q: query });
    const response = await fetch("https://html.duckduckgo.com/html/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
      body: formData.toString(),
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) return [];

    const html = await response.text();
    const results: Array<{ title: string; snippet: string; url: string }> = [];

    const resultMatches = html.matchAll(/<a[^>]+class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>/g);
    const snippetMatches = html.matchAll(/<a[^>]+class="result__snippet"[^>]*>([^<]*)<\/a>/g);

    const snippetArr = Array.from(snippetMatches).map(m => m[1].trim());
    let i = 0;

    for (const match of resultMatches) {
      if (results.length >= 5) break;
      results.push({
        url: match[1],
        title: match[2].trim(),
        snippet: snippetArr[i++] || "",
      });
    }

    return results;
  } catch (err) {
    logger.warn({ err }, "DuckDuckGo search failed");
    return [];
  }
}

export function formatSearchResults(results: Array<{ title: string; snippet: string; url: string }>): string {
  if (!results.length) return "I couldn't find relevant information.";
  return results
    .slice(0, 5)
    .map((r, i) => `${i + 1}. ${r.snippet || r.title}`)
    .join("\n\n");
}
