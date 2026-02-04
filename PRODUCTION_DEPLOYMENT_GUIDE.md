# Production Deployment Guide - Custom Domain + IP Restriction

## Overview

This guide covers:
1. ✅ Setting up custom subdomain (e.g., `docs.muletown.law`)
2. ✅ Restricting access to office IP address only
3. ✅ Testing and verification

---

## Part 1: Custom Domain Setup

### Option A: Subdomain (Recommended)

Using: `scrivening.muletown.law` (archaic term for legal document drafting - secure through obscurity!)

#### Step 1: Add DNS Record in Squarespace

1. **Log into Squarespace** at https://account.squarespace.com/
2. Go to **Settings** → **Domains** → Click on `muletown.law`
3. Click **DNS Settings** (or **Advanced DNS**)
4. Scroll to **Custom Records** section
5. Click **Add Record** or **Add**
6. Create a **CNAME record**:
   ```
   Type: CNAME
   Host: scrivening
   Data: cname.vercel-dns.com
   TTL: 3600 (or leave default - usually 1 hour)
   ```
7. Click **Save** or **Add Record**

**Important:** Don't include `.muletown.law` in the Host field - just `scrivening`

#### Step 2: Add Domain in Vercel

1. **Log into Vercel** (https://vercel.com/dashboard)
2. Click on your **muletownlaw-legal-docs** project
3. Click **Settings** tab → **Domains** section
4. Click **Add Domain** button
5. Enter exactly: `scrivening.muletown.law`
6. Click **Add**
7. Vercel will verify the DNS record (may take 1-10 minutes)
8. Once verified, you'll see ✅ next to the domain
9. SSL certificate will auto-provision (another 5-10 minutes)

#### Step 3: Wait for SSL Certificate

- Vercel automatically provisions a free SSL certificate
- Takes 5-10 minutes
- You'll receive an email when ready

---

### Option B: Root Domain (Alternative)

Use the main domain `muletown.law` (not recommended if already used)

**Note:** Only do this if you're NOT using `muletown.law` for your main website.

#### DNS Changes (Squarespace):
```
Type: A Record
Host: @ (root)
Data: 76.76.21.21
TTL: 3600
```

Then add domain in Vercel as `muletown.law`

---

## Part 2: IP Restriction

### Option 1: Vercel Edge Middleware (Recommended - Free)

Add IP restriction directly in your Vercel project.

#### Step 1: Create Middleware File

Create file: `middleware.js` in the root of your repo:

```javascript
// middleware.js
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
  // Your office IP address(es)
  const ALLOWED_IPS = [
    '123.45.67.89',  // Replace with your office IP
    // Add more IPs if needed:
    // '123.45.67.90',  // VPN IP
    // '123.45.67.91',  // Backup office
  ];

  // Get client IP
  const clientIP = request.headers.get('x-real-ip')
    || request.headers.get('x-forwarded-for')?.split(',')[0].trim()
    || 'unknown';

  console.log(`Access attempt from IP: ${clientIP}`);

  // Check if IP is allowed
  if (!ALLOWED_IPS.includes(clientIP)) {
    return new Response(
      `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Access Restricted</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
              display: flex;
              justify-content: center;
              align-items: center;
              height: 100vh;
              margin: 0;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
              background: white;
              padding: 3rem;
              border-radius: 12px;
              box-shadow: 0 20px 60px rgba(0,0,0,0.3);
              text-align: center;
              max-width: 500px;
            }
            h1 { color: #333; margin: 0 0 1rem 0; }
            p { color: #666; line-height: 1.6; }
            .ip {
              background: #f0f0f0;
              padding: 0.5rem 1rem;
              border-radius: 6px;
              font-family: monospace;
              margin: 1rem 0;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>🔒 Access Restricted</h1>
            <p>This document generation system is only accessible from authorized Muletown Law office locations.</p>
            <div class="ip">Your IP: ${clientIP}</div>
            <p>If you believe you should have access, please contact IT support.</p>
          </div>
        </body>
      </html>
      `,
      {
        status: 403,
        headers: {
          'Content-Type': 'text/html',
        },
      }
    );
  }

  // IP is allowed, continue
  return;
}
```

#### Step 2: Find Your Office IP Address

**From your office computer:**
1. Go to https://whatismyipaddress.com/
2. Copy the **IPv4 address** shown
3. Replace `123.45.67.89` in the middleware with your actual IP

**Example:**
```javascript
const ALLOWED_IPS = [
  '203.0.113.42',  // Muletown Law Office
];
```

#### Step 3: Deploy

```bash
git add middleware.js
git commit -m "Add IP restriction middleware"
git push origin main
```

---

### Option 2: Vercel Firewall (Requires Pro Plan - $20/month)

If you have Vercel Pro plan:

1. Go to Vercel Dashboard → Project Settings
2. Click **Firewall**
3. Click **IP Blocking**
4. Set to **Allow only specific IPs**
5. Add your office IP: `123.45.67.89`
6. Click **Save**

---

## Part 3: Testing

### Test IP Restriction

#### From Office (Should Work):
1. Visit `https://docs.muletown.law`
2. Should load normally
3. Try generating a document
4. Should work perfectly

#### From Home/Phone (Should Block):
1. Disconnect from office WiFi / use mobile data
2. Visit `https://docs.muletown.law`
3. Should see "Access Restricted" message
4. Should NOT be able to access any pages

### Test Document Generation

Generate a test document for each type:
- ✅ POA: Should download as `2026-02-04 POA Hutto Thomas.docx`
- ✅ ACP: Should download as `2026-02-04 ACP Hutto Thomas.docx`
- ✅ HCPOA: Should download as `2026-02-04 HCPOA Hutto Thomas.docx`
- ✅ Will: Should download as `2026-02-04 LWT Hutto Thomas.docx`

---

## Part 4: Common Issues & Solutions

### Issue: "Your IP: unknown"

**Cause:** Vercel headers not being passed correctly

**Solution:** Update middleware to check multiple header sources:
```javascript
const clientIP =
  request.headers.get('x-real-ip') ||
  request.headers.get('x-forwarded-for')?.split(',')[0].trim() ||
  request.ip ||
  'unknown';
```

### Issue: Blocked at office

**Cause:** Office IP changed (happens with dynamic IPs)

**Solution:**
1. Check current IP at https://whatismyipaddress.com/
2. Update `middleware.js` with new IP
3. Commit and push

**Better Solution:** Use a static IP from your ISP or VPN

### Issue: DNS not propagating

**Cause:** DNS changes can take up to 48 hours

**Solution:**
1. Wait 30 minutes
2. Check DNS with: https://dnschecker.org/
3. Enter `docs.muletown.law` and verify CNAME record

### Issue: SSL certificate error

**Cause:** Vercel still provisioning certificate

**Solution:** Wait 10 minutes and try again

---

## Part 5: Maintenance

### Adding New Authorized IPs

If staff work from home or you have multiple offices:

1. Edit `middleware.js`
2. Add new IP to array:
```javascript
const ALLOWED_IPS = [
  '203.0.113.42',  // Main Office
  '203.0.113.43',  // Remote Office
  '198.51.100.10', // VPN IP
];
```
3. Commit and push

### Temporarily Allowing Access

To temporarily disable IP restriction (e.g., for testing):

1. Comment out the IP check in `middleware.js`:
```javascript
// Temporarily allow all IPs
// if (!ALLOWED_IPS.includes(clientIP)) {
//   return new Response(...);
// }
```
2. Commit and push
3. **Remember to re-enable later!**

---

## Quick Start Checklist

- [ ] **Step 1:** Add CNAME record in Squarespace DNS
- [ ] **Step 2:** Add domain in Vercel settings
- [ ] **Step 3:** Wait for SSL certificate (5-10 min)
- [ ] **Step 4:** Find office IP address
- [ ] **Step 5:** Create `middleware.js` with office IP
- [ ] **Step 6:** Commit and push middleware
- [ ] **Step 7:** Test from office (should work)
- [ ] **Step 8:** Test from phone/home (should block)
- [ ] **Step 9:** Generate test documents
- [ ] **Step 10:** Update staff on new URL

---

## URLs After Setup

**Old (Vercel):** `https://muletownlaw-legal-docs.vercel.app` (will still work)
**New (Custom):** `https://docs.muletown.law` (IP restricted)

**Recommended:** Redirect old URL to new URL in Vercel settings.

---

## Security Best Practices

1. ✅ Always use HTTPS (automatic with Vercel)
2. ✅ Keep office IP list up to date
3. ✅ Use static IP if possible
4. ✅ Monitor access logs in Vercel dashboard
5. ✅ Review IP list monthly
6. ✅ Consider adding VPN IP as backup

---

## Cost Summary

**Squarespace:** No additional cost (included in domain)
**Vercel Hobby (Free):** $0/month with middleware IP restriction
**Vercel Pro (Optional):** $20/month for built-in firewall

**Recommended:** Start with free Hobby + middleware, upgrade if needed.

---

## Support

**Squarespace DNS Help:** https://support.squarespace.com/hc/en-us/articles/205812378
**Vercel Custom Domains:** https://vercel.com/docs/concepts/projects/domains
**Vercel Middleware:** https://vercel.com/docs/functions/edge-middleware

---

**Estimated setup time: 20-30 minutes**
**Result: Secure, professional, internal document system** ✅
