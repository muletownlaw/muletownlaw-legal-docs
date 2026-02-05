// IP Restriction Middleware for Muletown Law Document System
// This restricts access to only authorized office IP addresses

export const config = {
  matcher: [
    /*
     * Match all request paths
     * This runs on EVERY request to check IP
     */
    '/(.*)',
  ],
}

export function middleware(request) {
  // Skip middleware for debug page
  if (request.nextUrl.pathname === '/debug-ip.html') {
    return;
  }

  // Muletown Law Office IP Address
  // Detected: February 4, 2026
  const ALLOWED_IPS = [
    '66.211.23.74',  // Muletown Law Office - Columbia, TN
    // Add more IPs if needed (multiple offices, VPN, staff working remotely):
    // '203.0.113.43',  // Remote office
    // '198.51.100.10', // VPN IP
  ];

  // Get client IP from various possible headers - try all methods
  const forwardedFor = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  const cfConnectingIP = request.headers.get('cf-connecting-ip'); // Cloudflare

  const clientIP = cfConnectingIP
    || realIP
    || (forwardedFor ? forwardedFor.split(',')[0].trim() : null)
    || request.ip
    || 'unknown';

  // Log access attempts (visible in Vercel logs)
  console.log(`[IP Check] Access from: ${clientIP} | Path: ${request.nextUrl.pathname}`);
  console.log(`[IP Check] Headers - x-forwarded-for: ${forwardedFor}, x-real-ip: ${realIP}, cf-connecting-ip: ${cfConnectingIP}`);

  // Check if IP is in allowed list
  if (!ALLOWED_IPS.includes(clientIP)) {
    console.log(`[IP Check] BLOCKED - Redirecting ${clientIP} to muletown.law`);

    // Redirect to estate planning page
    return Response.redirect('https://www.muletown.law/estate-planning', 302);
  }

  // IP is allowed, continue to requested page
  console.log(`[IP Check] ALLOWED - ${clientIP}`);
  return;
}
