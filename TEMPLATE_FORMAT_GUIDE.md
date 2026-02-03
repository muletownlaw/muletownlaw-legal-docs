# Template Format Guide

## How to Create Templates with Placeholders

Your Word templates should be properly formatted legal documents with placeholders that the system will replace with actual client data.

---

## Example: Power of Attorney Template

```
Prepared by:
Muletown Law, P.C.
1109 S Garden Street
Columbia, TN 38401

DURABLE GENERAL POWER OF ATTORNEY

I, {CLIENT_NAME}, a resident of {COUNTY} County, Tennessee do hereby 
make, constitute and appoint my {AIF_RELATIONSHIP}, {AIF_NAME} as my 
attorney-in-fact. If my said {AIF_RELATIONSHIP} is unwilling or unable 
to serve in said capacity, then I appoint my {ALTERNATE_AIF_RELATIONSHIP}, 
{ALTERNATE_AIF_NAME}, as my alternate attorney-in-fact under the Uniform 
Durable Power of Attorney Act (T.C.A. § 34-6-101, et seq.) and in my 
name and stead to:

I. GENERAL AUTHORITY

1. Generally, do, sign or perform in the principal's name, place and 
   stead any act, deed, matter or thing whatsoever...

[Continue with rest of template]

WITNESS MY SIGNATURE THIS _________ DAY OF {EXEC_MONTH}, {EXEC_YEAR}.

_________________________________
{CLIENT_NAME}

STATE OF TENNESSEE
COUNTY OF {COUNTY}

Personally, appeared before me, the undersigned a Notary Public in and 
for the state and county aforesaid, the within named {CLIENT_NAME} with 
whom I am personally acquainted, and who acknowledged that {PRONOUN_SUBJECTIVE} 
executed the foregoing instrument for the purposes therein contained.

WITNESS my hand and official seal at office in Maury County, Tennessee, 
this _________ day of {EXEC_MONTH}, {EXEC_YEAR}.

_________________________________
NOTARY PUBLIC

My Commission Expires: _____________________
```

---

## Example: Last Will and Testament Template

```
LAST WILL AND TESTAMENT
OF
{CLIENT_NAME}

I, {CLIENT_NAME}, a resident of {COUNTY} County, Tennessee, being of 
sound mind and disposing memory, do hereby make, publish, and declare 
this to be my Last Will and Testament, hereby expressly revoking any 
and all Wills and Codicils by me at any time heretofore made.

ARTICLE I
IDENTIFICATION AND DECLARATIONS

I am married to {SN_BENEFICIARY}. [If applicable: I have __ children: 
names will be inserted during generation]

ARTICLE II
DISPOSITION OF ESTATE

I give, devise, and bequeath all of my property, real, personal and 
mixed, of whatever kind and wherever situated, which I may own or have 
the right to dispose of at the time of my death, to my spouse, 
{SN_BENEFICIARY}, if {PRONOUN_SUBJECTIVE} survives me by thirty (30) days.

In the event my said spouse does not survive me by thirty (30) days, 
then I give, devise, and bequeath all of my property to my children 
[names inserted during generation], in equal shares, per stirpes.

ARTICLE III
APPOINTMENT OF EXECUTOR

I hereby nominate and appoint {PRIMARY_EXECUTOR} to serve as Executor 
of this my Last Will and Testament. In the event {PRIMARY_EXECUTOR} 
fails to qualify or ceases to serve, then I nominate and appoint 
{ALTERNATE_EXECUTOR} to serve as alternate Executor.

[Continue with remaining articles]

IN WITNESS WHEREOF, I have hereunto set my hand and seal this {EXEC_DAY} 
day of {EXEC_MONTH}, {EXEC_YEAR}.

_________________________________
{CLIENT_NAME}, Testator/Testatrix

WITNESS ATTESTATION

WITNESS (PRINT NAME):  _________________________________

WITNESS (SIGNATURE):   _________________________________

WITNESS (PRINT NAME):  _________________________________

WITNESS (SIGNATURE):   _________________________________

SELF-PROVING AFFIDAVIT

STATE OF TENNESSEE
COUNTY OF {COUNTY}

We, the undersigned, being first duly sworn, make oath that {CLIENT_NAME} 
on the day and date above written, declared and signified to us that the 
above instrument is {PRONOUN_POSSESSIVE} Last Will and Testament...

[Continue with affidavit]
```

---

## Formatting Best Practices

### 1. Use Word Styles (Important!)
- **Headers**: Use "Heading 1" for article titles
- **Body Text**: Use "Normal" style
- **Signature Lines**: Use underline formatting
- **Bold**: Use for names and important terms

### 2. Placeholder Guidelines
- Always use curly braces: `{PLACEHOLDER}`
- ALL CAPS for placeholder names
- No spaces inside braces
- Case-sensitive

### 3. Keep Original Formatting
When editing templates:
- Don't delete and retype text with placeholders
- Select text → Type new text (preserves formatting)
- Use Find & Replace when possible

### 4. Dynamic Content (Children, Bequests)
Some content is generated dynamically (like lists of children).
Mark these sections with comments:

```
[CHILDREN_LIST_WILL_BE_INSERTED_HERE]
```

The Python code will handle inserting:
- Child names with proper formatting
- Relationship terms (son/daughter)
- Birth dates
- Proper grammar (commas, "and")

---

## Testing Your Template

### Before Uploading to Google Drive:

1. **Check all placeholders:**
   - Search for `{` in your document
   - Verify each placeholder matches template_config.py

2. **Test formatting:**
   - Bold should be bold
   - Headers should be styled as headers
   - Underlines should be underlined

3. **Verify legal content:**
   - All required clauses present
   - Proper Tennessee law references
   - Correct statutory citations

### After Uploading:

1. Generate a test document with fake data
2. Open in Word
3. Check:
   - All placeholders replaced?
   - Formatting preserved?
   - No extra {braces} left?
   - Grammar correct?

---

## Common Mistakes to Avoid

❌ **Wrong:** `{ CLIENT_NAME }` (spaces inside braces)
✅ **Correct:** `{CLIENT_NAME}`

❌ **Wrong:** `{client_name}` (lowercase)
✅ **Correct:** `{CLIENT_NAME}`

❌ **Wrong:** `[CLIENT_NAME]` (square brackets)
✅ **Correct:** `{CLIENT_NAME}`

❌ **Wrong:** Deleting text and retyping with placeholder
✅ **Correct:** Select text → Replace with placeholder (keeps formatting)

---

## Placeholder Reference

### Client Information
- `{CLIENT_NAME}` - Full name (will be uppercase in output)
- `{CLIENT_GENDER}` - Male or Female
- `{SN_BENEFICIARY}` - Spouse name
- `{COUNTY}` - County name
- `{EXEC_DAY}` - Day of execution (1st, 2nd, 3rd, etc.)
- `{EXEC_MONTH}` - Month of execution
- `{EXEC_YEAR}` - Year of execution

### Pronouns (Auto-generated based on gender)
- `{PRONOUN_SUBJECTIVE}` - he/she
- `{PRONOUN_POSSESSIVE}` - his/her
- `{PRONOUN_OBJECTIVE}` - him/her

### Power of Attorney
- `{AIF_NAME}` - Attorney-in-fact name
- `{AIF_RELATIONSHIP}` - Relationship (wife, husband, daughter, son, etc.)
- `{ALTERNATE_AIF_NAME}` - Alternate AIF name
- `{ALTERNATE_AIF_RELATIONSHIP}` - Alternate relationship

### Last Will and Testament
- `{PRIMARY_EXECUTOR}` - Primary executor name
- `{ALTERNATE_EXECUTOR}` - Alternate executor name
- `{SN_BENEFICIARY_GENDER}` - Spouse gender

---

## Need Help?

If you're unsure about template format:
1. Check existing working templates in project
2. Review this guide
3. Test with fake data before using with clients
4. Keep backups of templates before major changes

---

**Ready to create your templates?**
1. Open Word or Google Docs
2. Create your legal document
3. Replace variable content with placeholders
4. Save as .docx
5. Upload to Google Drive
6. Follow GOOGLE_DRIVE_SETUP.md
