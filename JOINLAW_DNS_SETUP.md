# join.law DNS Setup Guide - scrivening.muletown.law

## Quick Reference

**Domain Registrar:** join.law (legal-specific domain service)
**Subdomain:** scrivening.muletown.law
**Purpose:** Custom URL for internal document generation system

---

## Step-by-Step Instructions

### Step 1: Log into join.law

1. Go to https://join.law/ (or https://manage.join.law/)
2. Log in with your join.law credentials
3. You should see your domain dashboard

---

### Step 2: Navigate to DNS Management

The exact path depends on join.law's interface, but typically:

**Option A - Most Common:**
1. Click on **muletown.law** (your domain)
2. Look for **DNS** or **DNS Management** or **DNS Settings**
3. Click to manage DNS records

**Option B - If using cPanel/WHM:**
1. Find **Domain Management** or **DNS Zone Editor**
2. Select **muletown.law**
3. Click **Manage** or **Edit Zone**

**Option C - If different interface:**
1. Look for: **Domains** → **Manage** → **DNS**
2. Or: **Advanced** → **DNS Records**

---

### Step 3: Add CNAME Record

Once in DNS management:

1. **Look for "Add Record" button**
   - Might say "Add DNS Record", "Add New Record", or just "Add"

2. **Select Record Type:**
   - Choose `CNAME` from dropdown

3. **Fill in the form:**

   | Field Name | What to Enter | Notes |
   |------------|---------------|-------|
   | **Type** | `CNAME` | Select from dropdown |
   | **Name** or **Host** | `scrivening` | Just the subdomain name |
   | **Target** or **Points to** or **Value** | `cname.vercel-dns.com` | Vercel's CNAME endpoint |
   | **TTL** | `3600` or `1 hour` | Can leave as default |

   **CRITICAL - Common Mistakes to Avoid:**
   - ❌ DON'T enter: `scrivening.muletown.law` in Name field
   - ✅ DO enter: `scrivening`
   - ❌ DON'T add `https://` or trailing `.`
   - ✅ DO enter exactly: `cname.vercel-dns.com`

4. **Save the record**
   - Click "Save", "Add Record", or "Create"

---

### Step 4: Verify the Record

After saving, you should see your new record in the DNS list:

```
Type: CNAME
Name: scrivening (or scrivening.muletown.law)
Target: cname.vercel-dns.com
TTL: 3600
```

---

## join.law Specific Notes

### If join.law uses cPanel:
- Go to **DNS Zone Editor**
- Click **Manage** next to muletown.law
- Click **Add Record**
- Select CNAME from type dropdown

### If join.law uses Plesk:
- Go to **DNS Settings**
- Click **Add Record**
- Choose CNAME record type

### If you see "Advanced DNS":
- This is the right place
- Follow the add record process above

---

## Common join.law Interface Variations

### Variation 1: Simple Form
```
Record Type: [CNAME ▼]
Host: scrivening
Points To: cname.vercel-dns.com
TTL: [3600]
[Save]
```

### Variation 2: Detailed Form
```
Record Type: [CNAME ▼]
Name: scrivening
FQDN: (auto-fills to scrivening.muletown.law)
Target: cname.vercel-dns.com
TTL: [Auto ▼] or [3600]
[Add Record]
```

### Variation 3: Zone File Editor
If you see a text editor with zone file syntax:
```
scrivening    IN    CNAME    cname.vercel-dns.com.
```
(Note the trailing dot after .com)

---

## Troubleshooting

### "Cannot add CNAME for existing record"
- A `scrivening` subdomain already exists
- Delete the old record first, or choose different subdomain

### "Invalid CNAME target"
- Make sure you entered: `cname.vercel-dns.com`
- No `http://`, no trailing spaces
- Exactly as shown

### "Permission denied" or "Access restricted"
- You may need admin/owner access
- Ask the account owner to add you as DNS manager
- Or have them add the record for you

### "Can't find DNS settings"
- join.law might use a custom control panel
- Try searching for "DNS", "Domain Management", or "Zone Editor"
- Contact join.law support if stuck: support@join.law

---

## Check DNS Propagation

After adding the record:

1. **Wait 5-10 minutes**

2. **Check if it's working:**
   - Go to https://dnschecker.org/
   - Enter: `scrivening.muletown.law`
   - Select: `CNAME` from type dropdown
   - Click "Search DNS"
   - Look for: `cname.vercel-dns.com` in results

3. **If not showing yet:**
   - Wait another 10-15 minutes
   - DNS can take up to 48 hours (usually much faster)
   - Average wait time: 15-30 minutes

---

## After DNS Propagates

Once the CNAME is visible in DNS checker:

1. Move to Vercel configuration
2. Add domain in Vercel dashboard
3. Vercel will auto-verify the CNAME
4. SSL certificate will be provisioned automatically

See: **PRODUCTION_DEPLOYMENT_GUIDE.md** → Part 1 → Step 2

---

## join.law Support

**If you get stuck:**

- **Support Email:** support@join.law
- **Phone:** Check your join.law account for support number
- **Documentation:** https://join.law/support (if available)
- **Live Chat:** May be available in your join.law dashboard

**What to ask:**
> "I need to add a CNAME record for the subdomain 'scrivening' pointing to 'cname.vercel-dns.com' for muletown.law. Can you help me find the DNS management section?"

---

## Quick Checklist

Before moving to Vercel:

- [ ] Logged into join.law
- [ ] Found DNS management for muletown.law
- [ ] Added CNAME record:
  - [ ] Name/Host: `scrivening`
  - [ ] Target/Points to: `cname.vercel-dns.com`
  - [ ] TTL: 3600 (or default)
- [ ] Record saved successfully
- [ ] Visible in DNS records list
- [ ] Verified with dnschecker.org (optional but recommended)

---

## Summary

**What we're doing:**
Creating a subdomain (`scrivening.muletown.law`) that points to Vercel's servers

**Why CNAME:**
Allows Vercel to handle the hosting while you keep control of your domain

**Next step:**
Once this DNS record is active (10-30 minutes), we'll add the domain in Vercel

---

**Estimated time:** 5-10 minutes to add record + 10-30 minutes for propagation
**Next:** Vercel domain configuration (2 minutes)
