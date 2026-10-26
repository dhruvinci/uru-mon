/**
 * Vercel Web Analytics only sees page loads, and the whole game is one page, so every visit counted as a bounce and
 * nothing showed what people did. Each section of the game is reported as a page of its own instead (the address bar
 * doesn't change), at most once per visit: every page view counts towards the free plan's 50,000 events a month.
 *
 * `window.va` is the queue index.html sets up. Off localhost Vercel's script sends what's queued; on localhost the
 * script isn't loaded, so calls just collect in `window.vaq` (which the tests read). Automated browsers aren't counted.
 */
const sent = new Set();

/** @param {string} path e.g. '/quick-battle' */
export function trackPage(path) {
  if (sent.has(path)) {
    return;
  }
  sent.add(path);
  try {
    window.va?.('pageview', { route: path, path });
  } catch {
    // analytics must never get in the way of the game
  }
}
