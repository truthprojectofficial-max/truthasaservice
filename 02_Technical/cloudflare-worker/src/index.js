/**
 * Cloudflare Worker — OrderGetItRight update server
 *
 * Routes:
 *   GET /:platform/:clientVersion
 *     Returns the updater manifest JSON that Tauri's updater expects,
 *     or 204 No Content if the client is already up-to-date.
 *
 *   GET /latest
 *     Returns the most recent release metadata as JSON.
 *
 *   GET /health
 *     Returns "OK" for liveness checks.
 *
 * Data source: Cloudflare KV namespace `UPDATES_KV`.
 *   - Key: `latest_release` -> JSON object:
 *       {
 *         "version": "0.1.0",
 *         "pub_date": "2026-07-24T12:00:00Z",
 *         "notes": "Initial release.",
 *         "platforms": {
 *           "windows-x86_64": {
 *             "url": "https://r2.ordergetitright.com/ordergetitright-releases/windows-x86_64/OrderGetItRight_0.1.0_x64-setup.exe",
 *             "signature": "<base64 tauri signature>"
 *           },
 *           "darwin-aarch64": { ... },
 *           "darwin-x86_64":  { ... },
 *           "linux-x86_64":   { ... }
 *         }
 *       }
 *
 * Per the OGIR GTM plan (.hermes/plans/2026-07-24_ogir-gtm-fix-plan.md),
 * the Worker is deployed to `update.ordergetitright.com` and serves
 * the updater manifest for all 4 platforms.
 *
 * Operator deploys: `cd 02_Technical/cloudflare-worker && wrangler deploy`
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, '');  // strip trailing slash

    // Health check
    if (path === '/health' || path === '') {
      return new Response('OK', {
        status: 200,
        headers: { 'Content-Type': 'text/plain' },
      });
    }

    // /latest -> the most recent release metadata
    if (path === '/latest') {
      const latest = await env.UPDATES_KV.get('latest_release', { type: 'json' });
      if (!latest) {
        return new Response('No releases published yet', { status: 204 });
      }
      return new Response(JSON.stringify(latest, null, 2), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // /:platform/:clientVersion -> updater manifest for Tauri
    // Tauri's updater GETs this URL on app launch to check for updates.
    const m = path.match(/^\/([^\/]+)\/([0-9]+\.[0-9]+\.[0-9]+)$/);
    if (m) {
      const [, targetPlatform, clientVersion] = m;

      const latest = await env.UPDATES_KV.get('latest_release', { type: 'json' });
      if (!latest) {
        return new Response('', { status: 204 });
      }

      // Client is already up-to-date
      if (latest.version === clientVersion) {
        return new Response('', { status: 204 });
      }

      // Get the platform-specific download
      const platformData = latest.platforms?.[targetPlatform];
      if (!platformData) {
        return new Response(`Platform ${targetPlatform} not found`, { status: 404 });
      }

      // Return the manifest Tauri expects:
      //   { version, pub_date, url, signature, notes }
      const manifest = {
        version: latest.version,
        pub_date: latest.pub_date,
        url: platformData.url,
        signature: platformData.signature,
        notes: latest.notes,
      };
      return new Response(JSON.stringify(manifest), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // /releases/* — serve binary downloads from R2 bucket
    if (path.startsWith('/releases/')) {
      const key = path.slice('/releases/'.length);
      const object = await env.RELEASES_BUCKET.get(key);
      if (!object) {
        return new Response('File not found in R2: ' + key, { status: 404 });
      }
      const headers = new Headers();
      object.writeHttpMetadata(headers);
      headers.set('Content-Type', object.httpMetadata?.contentType || 'application/octet-stream');
      headers.set('Content-Disposition', 'attachment');
      return new Response(object.body, { status: 200, headers });
    }

    // Fallback: 404
    return new Response('Not found', { status: 404 });
  },
};
