// Wrapper for Vercel Analytics
// The analytics script is vendored in src/lib/vendor/vercel-analytics.mjs
import { inject, track, pageview } from './vendor/vercel-analytics.mjs';

export { inject, track, pageview };
