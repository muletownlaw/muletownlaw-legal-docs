# Squarespace DNS Setup Guide - scrivening.muletown.law

## Step-by-Step Instructions with Troubleshooting

### Part 1: Log into Squarespace

1. Go to https://account.squarespace.com/
2. Log in with your Squarespace credentials
3. You should see your website dashboard

---

### Part 2: Navigate to DNS Settings

**Option A - If you see a "Domains" menu:**
1. Click **Settings** (usually in left sidebar)
2. Click **Domains**
3. Click on **muletown.law** (your domain)
4. Look for **DNS Settings** or **Advanced DNS** button
5. Click it

**Option B - If layout is different:**
1. Click **Settings**
2. Look for **Domains** section
3. Click **Advanced** or **DNS** next to muletown.law
4. Click **DNS Settings** or **Manage DNS**

---

### Part 3: Add the CNAME Record

Once you're in DNS Settings:

1. **Scroll down** to find **Custom Records** or **DNS Records** section
   - You might see existing records (A records, MX records, etc.)
   - Don't touch those!

2. **Click "Add Record"** or **"Add"** button
   - Should be near the top or bottom of the records list

3. **Fill in the form:**

   | Field | What to Enter |
   |-------|---------------|
   | **Type** | Select `CNAME` from dropdown |
   | **Host** or **Name** | `scrivening` (just the word, no dots) |
   | **Data** or **Points to** | `cname.vercel-dns.com` |
   | **TTL** | `3600` or leave default (might say "Auto" or "1 hour") |

4. **Double-check:**
   - Host: `scrivening` ✅
   - Data: `cname.vercel-dns.com` ✅
   - No extra dots or spaces ✅

5. **Click "Save" or "Add Record"**

---

### Part 4: Verify It Saved

After saving, you should see the new record in your DNS list:

```
Type: CNAME
Name: scrivening
Value: cname.vercel-dns.com
TTL: 3600 (or 1h)
```

---

## Common Squarespace Interface Variations

### Squarespace 7.0:
- Settings → Domains → Advanced → DNS Settings → Add Record

### Squarespace 7.1:
- Settings → Domains → Click domain name → DNS Settings → Add Record

### Google Domains (if migrated):
- Might say "DNS" instead of "DNS Settings"
- Process is the same

---

## Troubleshooting

### "Can't find DNS Settings"

If you can't find DNS Settings:
1. Make sure you're logged in as the domain **owner** (not just editor)
2. Try clicking the domain name itself (`muletown.law`)
3. Look for tabs like "Advanced", "DNS", or "Settings"
4. Contact Squarespace support if still stuck

### "CNAME record already exists"

If you see an error about existing CNAME:
- There's already a `scrivening` subdomain configured
- Either delete the old one first, OR
- Choose a different subdomain name (e.g., `scrivenwork`, `drafting`, etc.)

### "Invalid CNAME target"

Double-check the data field:
- Should be: `cname.vercel-dns.com`
- NOT: `https://cname.vercel-dns.com`
- NOT: `cname.vercel-dns.com.`
- Common mistake: adding `https://` or extra dots

### "Permission denied"

You might not have domain admin access:
- Ask the account owner to add the record
- Or get them to give you admin permissions

---

## After Adding the Record

### What happens next:

1. **DNS propagation** (5-30 minutes)
   - Your change spreads across the internet
   - During this time, some people see the old setting, some see new
   - This is normal!

2. **Check propagation status:**
   - Go to https://dnschecker.org/
   - Enter: `scrivening.muletown.law`
   - Select: `CNAME` from dropdown
   - Click "Search"
   - Should show `cname.vercel-dns.com` in results
   - If not showing yet, wait 10 more minutes

3. **Once propagated:**
   - Move to Vercel setup (next step)
   - Vercel will verify the CNAME automatically

---

## Visual Reference

Your DNS records should look something like this after adding:

```
[Existing Records - DON'T TOUCH]
Type: A      Name: @           Value: 198.185.159.144
Type: A      Name: www         Value: 198.185.159.144
Type: MX     Name: @           Value: mx.example.com

[NEW RECORD - WHAT YOU'RE ADDING]
Type: CNAME  Name: scrivening  Value: cname.vercel-dns.com  ← This one!

[Other existing records...]
```

---

## Quick Checklist

Before moving to Vercel setup, verify:

- [ ] Logged into Squarespace as domain owner
- [ ] Found DNS Settings for muletown.law
- [ ] Added CNAME record with:
  - [ ] Host: `scrivening`
  - [ ] Data: `cname.vercel-dns.com`
- [ ] Record saved successfully
- [ ] Can see it in the DNS records list

---

## Next Step: Vercel Configuration

Once the CNAME is added and saved in Squarespace:

1. Wait 5-10 minutes for DNS propagation
2. Go to Vercel (https://vercel.com/dashboard)
3. Follow the Vercel setup steps in PRODUCTION_DEPLOYMENT_GUIDE.md

---

## Need Help?

**Squarespace Support:**
- Live chat: https://support.squarespace.com/
- Phone: Usually available during business hours

**Alternative:**
If completely stuck, you can temporarily skip the custom domain and just use the IP-restricted Vercel URL until we sort out the DNS.

---

**Estimated time: 5-10 minutes**
**Next: Vercel domain configuration**
