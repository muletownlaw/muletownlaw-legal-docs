export default function middleware(request) {
  const url = new URL(request.url);

  // Skip debug page
  if (url.pathname === '/debug-ip.html') {
    return;
  }

  // Muletown Law Office IP
  const ALLOWED_IPS = ['66.211.23.74'];

  // Get client IP
  const clientIP = request.headers.get('x-forwarded-for')?.split(',')[0].trim() || 'unknown';

  console.log(`[IP] ${clientIP} → ${url.pathname}`);

  // Block unauthorized
  if (!ALLOWED_IPS.includes(clientIP)) {
    return Response.redirect('https://www.muletown.law/estate-planning', 302);
  }
}
