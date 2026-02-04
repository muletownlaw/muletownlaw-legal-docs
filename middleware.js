// IP Restriction Middleware for Muletown Law Document System
// This restricts access to only authorized office IP addresses

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}

export function middleware(request) {
  // Muletown Law Office IP Address
  // Detected: February 4, 2026
  const ALLOWED_IPS = [
    '66.211.23.74',  // Muletown Law Office - Columbia, TN
    // Add more IPs if needed (multiple offices, VPN, staff working remotely):
    // '203.0.113.43',  // Remote office
    // '198.51.100.10', // VPN IP
  ];

  // Get client IP from various possible headers
  const clientIP = request.headers.get('x-real-ip')
    || request.headers.get('x-forwarded-for')?.split(',')[0].trim()
    || request.ip
    || 'unknown';

  // Log access attempts (visible in Vercel logs)
  console.log(`[IP Check] Access attempt from: ${clientIP}`);

  // Check if IP is in allowed list
  if (!ALLOWED_IPS.includes(clientIP)) {
    console.log(`[IP Check] BLOCKED - ${clientIP} not in allowed list`);

    return new Response(
      `
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Access Restricted - Muletown Law</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 100vh;
              margin: 0;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              padding: 1rem;
            }
            .container {
              background: white;
              padding: 3rem;
              border-radius: 12px;
              box-shadow: 0 20px 60px rgba(0,0,0,0.3);
              text-align: center;
              max-width: 500px;
              width: 100%;
            }
            .icon {
              font-size: 4rem;
              margin-bottom: 1rem;
            }
            h1 {
              color: #333;
              margin: 0 0 1rem 0;
              font-size: 1.8rem;
            }
            p {
              color: #666;
              line-height: 1.6;
              margin: 1rem 0;
            }
            .ip-box {
              background: #f5f5f5;
              padding: 1rem;
              border-radius: 6px;
              font-family: 'Monaco', 'Courier New', monospace;
              margin: 1.5rem 0;
              border-left: 4px solid #667eea;
            }
            .ip-label {
              font-size: 0.85rem;
              color: #999;
              margin-bottom: 0.5rem;
            }
            .ip-value {
              font-size: 1.1rem;
              color: #333;
              font-weight: 600;
            }
            .footer {
              margin-top: 2rem;
              padding-top: 1.5rem;
              border-top: 1px solid #eee;
              font-size: 0.9rem;
              color: #999;
            }
            .contact {
              color: #667eea;
              text-decoration: none;
              font-weight: 600;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="icon">🔒</div>
            <h1>Access Restricted</h1>
            <p>This document generation system is only accessible from authorized Muletown Law office locations.</p>

            <div class="ip-box">
              <div class="ip-label">Your IP Address:</div>
              <div class="ip-value">${clientIP}</div>
            </div>

            <p>If you believe you should have access to this system, please contact the IT administrator with your IP address shown above.</p>

            <div class="footer">
              <strong>Muletown Law, P.C.</strong><br>
              Internal Document System
            </div>
          </div>
        </body>
      </html>
      `,
      {
        status: 403,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
        },
      }
    );
  }

  // IP is allowed, continue to requested page
  console.log(`[IP Check] ALLOWED - ${clientIP}`);
  return;
}
