# Google Drive Template Storage - Setup Guide

## Why Use Google Drive for Templates?

✅ **Easy Editing**: Edit templates directly in Google Docs or Word online
✅ **No GitHub Commits**: Template changes don't require code deployment
✅ **Instant Updates**: Changes reflect immediately in your app
✅ **Version History**: Google Drive tracks all changes automatically
✅ **Team Collaboration**: Share templates with staff easily
✅ **Free**: No additional costs

---

## Step-by-Step Setup

### Step 1: Upload Templates to Google Drive

1. **Create a folder in Google Drive:**
   - Go to https://drive.google.com
   - Click "New" → "Folder"
   - Name it: "Estate Planning Templates"

2. **Upload your template files:**
   - Drag and drop all your `.docx` files into this folder
   - Or click "New" → "File upload" and select files

3. **Recommended folder structure:**
   ```
   Estate Planning Templates/
   ├── Power of Attorney.docx
   ├── Last Will and Testament.docx
   ├── Healthcare POA.docx
   ├── Advance Care Plan.docx
   └── Clauses/
       ├── Handwritten List.docx
       ├── Love and Affection.docx
       ├── No Contest.docx
       └── ... (other clause templates)
   ```

---

### Step 2: Make Templates Accessible

**For each template file:**

1. **Right-click the file** → **"Share"**

2. **Click "Change to anyone with the link"**
   - Or if you want more security:
   - Click "Restricted" → "Anyone with the link"
   - Set to "Viewer" (read-only)

3. **Click "Copy link"**
   - You'll get a link like:
   ```
   https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing
   ```

4. **Extract the FILE_ID:**
   - The FILE_ID is the long string between `/d/` and `/view`
   - In the example above: `1a2b3c4d5e6f7g8h9i0j`

5. **Convert to direct download URL:**
   ```
   https://drive.google.com/uc?export=download&id=1a2b3c4d5e6f7g8h9i0j
   ```

---

### Step 3: Update Template Configuration

1. **Open `api/template_config.py` in your GitHub repository**

2. **Replace the placeholder FILE_IDs with your actual FILE_IDs:**

   ```python
   TEMPLATE_URLS = {
       'poa': 'https://drive.google.com/uc?export=download&id=YOUR_ACTUAL_FILE_ID',
       'will': 'https://drive.google.com/uc?export=download&id=YOUR_ACTUAL_FILE_ID',
       # ... etc
   }
   ```

3. **Save and commit to GitHub**
   - This will trigger automatic Vercel deployment

---

### Step 4: Prepare Your Templates with Placeholders

Your Word templates need to use specific placeholders that the system will replace with actual data.

**Example Power of Attorney template structure:**

```
DURABLE GENERAL POWER OF ATTORNEY

I, {CLIENT_NAME}, a resident of {COUNTY} County, Tennessee do hereby 
make, constitute and appoint my {AIF_RELATIONSHIP}, {AIF_NAME} as my 
attorney-in-fact...

[Rest of template content with placeholders]
```

**Available placeholders:**
- `{CLIENT_NAME}` - Client's full name
- `{COUNTY}` - County name
- `{AIF_NAME}` - Attorney-in-fact name
- `{AIF_RELATIONSHIP}` - Relationship (wife, husband, daughter, son)
- `{ALTERNATE_AIF_NAME}` - Alternate AIF name
- `{ALTERNATE_AIF_RELATIONSHIP}` - Alternate relationship
- `{EXEC_MONTH}` - Execution month
- `{EXEC_YEAR}` - Execution year
- `{PRONOUN_SUBJECTIVE}` - he/she
- `{PRONOUN_POSSESSIVE}` - his/her
- `{PRONOUN_OBJECTIVE}` - him/her

**For Last Will and Testament, add:**
- `{SN_BENEFICIARY}` - Spouse name
- `{PRIMARY_EXECUTOR}` - Primary executor name
- `{ALTERNATE_EXECUTOR}` - Alternate executor name
- `{EXEC_DAY}` - Execution day

---

### Step 5: Test Your Setup

1. **Visit your Vercel app**

2. **Fill out a test form** (use fake data)

3. **Generate a document**

4. **Open the downloaded document and verify:**
   - All placeholders were replaced
   - Formatting is preserved
   - Content is correct

---

## How to Update Templates (Day-to-Day Use)

### Making Template Changes:

1. **Open the template in Google Drive**
   - Double-click the file
   - It opens in Google Docs or Word Online

2. **Make your edits**
   - Fix typos
   - Update legal language
   - Modify formatting
   - Add/remove sections

3. **Save** (Ctrl+S or File → Save)

4. **Done!**
   - Next time someone generates a document, they get the updated version
   - No code changes needed
   - No GitHub commits required
   - No Vercel deployment needed

### Version History:

If you need to undo changes:
1. Right-click file → "Version history"
2. See all previous versions
3. Restore any previous version if needed

---

## Advantages Over GitHub Storage

| Feature | GitHub Storage | Google Drive Storage |
|---------|---------------|---------------------|
| **Edit Complexity** | Need to commit code | Edit in Word/Google Docs |
| **Deployment Time** | 2-3 minutes | Instant |
| **Version Control** | Yes | Yes (built-in) |
| **Team Access** | Need GitHub account | Just share link |
| **Non-technical Staff** | Difficult | Easy |
| **Update Speed** | Requires deployment | Immediate |

---

## Security Options

### Option 1: Public Links (Simplest)
- Anyone with link can view
- Best for: Internal use only
- Security: Medium

### Option 2: Google Service Account (Most Secure)
- Templates not publicly accessible
- Requires API credentials
- Best for: Production use with sensitive data
- Security: High

**For Service Account setup (optional advanced option):**
1. Create Google Cloud Project
2. Enable Google Drive API
3. Create Service Account
4. Share templates with service account email
5. Add credentials to Vercel environment variables

*Let me know if you want instructions for this option.*

---

## Troubleshooting

### "Template not found" error
- Check that FILE_ID is correct
- Verify file is shared ("Anyone with link can view")
- Make sure download URL format is correct

### Placeholders not being replaced
- Check spelling matches exactly (case-sensitive)
- Ensure placeholders are in curly braces `{PLACEHOLDER}`
- Verify placeholder is in template_config.py

### Formatting lost
- Use placeholder replacement in existing text
- Don't delete and retype - just replace text
- Preserve Word styles when editing

---

## Support

Questions? Check:
1. This guide
2. `template_config.py` for placeholder list
3. Example templates in Google Drive folder

---

**Ready to deploy?**
1. Upload templates to Google Drive
2. Get FILE_IDs
3. Update template_config.py
4. Commit to GitHub
5. Test on Vercel

**Estimated setup time: 15-20 minutes**
