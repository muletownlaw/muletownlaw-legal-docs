# Muletown Law Document Generator

A web-based document generation system for Tennessee legal documents, featuring:
- ✅ Last Will & Testament Generator
- ✅ Power of Attorney Generator
- ✅ Professional Word document output (.docx)
- ✅ Python-based serverless document generation

## 🏗️ Project Structure

```
vercel-project/
├── api/                    # Python serverless functions
│   └── generate-poa.py    # POA document generator
├── public/                 # Frontend HTML files
│   ├── index.html         # Landing page
│   ├── will.html          # Will generator interface
│   └── poa.html           # POA generator interface
├── templates/              # Document templates (future use)
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Quick Deployment

### Prerequisites
- GitHub account
- Vercel account (free tier is fine)

### Step 1: Upload to GitHub

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `muletown-law-docs` (or your preference)
   - Set to **Private** (recommended for client data)
   - Do NOT initialize with README, .gitignore, or license
   - Click "Create repository"

2. **Download this project folder** (you already have it)

3. **Upload files to GitHub:**
   
   **Option A: Upload via GitHub Web Interface (Easiest)**
   - On your new repository page, click "uploading an existing file"
   - Drag and drop ALL files from this project folder
   - Commit message: "Initial commit - Document generators"
   - Click "Commit changes"

   **Option B: Use Git Command Line**
   ```bash
   cd /path/to/vercel-project
   git init
   git add .
   git commit -m "Initial commit - Document generators"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/muletown-law-docs.git
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Sign up/Login to Vercel:**
   - Go to https://vercel.com/signup
   - Click "Continue with GitHub"
   - Authorize Vercel to access your GitHub

2. **Import your project:**
   - Click "Add New..." → "Project"
   - Find `muletown-law-docs` in your repository list
   - Click "Import"

3. **Configure the project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave default)
   - **Build Command:** Leave empty
   - **Output Directory:** Leave empty
   - Click "Deploy"

4. **Wait for deployment** (usually 30-60 seconds)

5. **Get your URL:**
   - Vercel will show you a URL like: `https://muletown-law-docs.vercel.app`
   - This is your live site!

### Step 3: Test Your Deployment

1. **Visit your URL** from Vercel
2. **Click on "Last Will & Testament"** or "Power of Attorney"
3. **Fill out the form**
4. **Click "Generate Document"**
5. **Download should start automatically** with a .docx file

## 📝 How It Works

### Frontend (HTML/JavaScript)
- Simple HTML forms collect user data
- JavaScript validates and sends data to API
- Triggers document download on success

### Backend (Python Serverless Functions)
- Vercel runs Python functions on-demand
- Uses `python-docx` library for professional Word documents
- Returns .docx files with proper formatting

### Document Generation Flow
```
User fills form → JavaScript validates → POST to /api/generate-poa
                                              ↓
                                    Python generates .docx
                                              ↓
                                    Returns document to browser
                                              ↓
                                    User downloads .docx file
```

## 🔧 Making Updates

### To Update HTML/Forms:
1. Edit files in `public/` folder
2. Commit and push to GitHub
3. Vercel auto-deploys (30 seconds)

### To Update Document Generation:
1. Edit files in `api/` folder
2. Commit and push to GitHub
3. Vercel auto-deploys (30-60 seconds)

### To Add New Document Type:
1. Create new HTML form in `public/` folder
2. Create new Python function in `api/` folder
3. Follow the pattern from `generate-poa.py`
## Template Management
   
   Templates are stored in Google Drive for easy editing by legal staff.
   
   - **Edit templates**: Open files in Google Drive
   - **Changes go live**: Immediately on save
   - **Version history**: Available in Google Drive
   
   See `docs/GOOGLE_DRIVE_SETUP.md` for details.
## 📦 Dependencies

- **python-docx** (1.1.0) - Word document generation
- **Vercel Python Runtime** - Serverless function hosting

## 🛠️ Troubleshooting

### Document not generating
- Check browser console (F12) for errors
- Verify all required fields are filled
- Check Vercel function logs (Vercel dashboard → Your project → Logs)

### Deployment failed
- Verify `vercel.json` is in root directory
- Check `requirements.txt` is present
- Ensure `api/` folder contains Python files

### Document format issues
- Edit the Python generator in `api/` folder
- Use `python-docx` documentation: https://python-docx.readthedocs.io/
- Test locally before deploying

## 🔒 Security Notes

- Set GitHub repository to **Private**
- Never commit API keys or sensitive data
- Consider adding authentication for production use
- Vercel provides HTTPS automatically

## 📚 Next Steps

1. **Add more document types** (Trusts, Deeds, etc.)
2. **Integrate with Lawmatics API** for matter data
3. **Add user authentication** (if needed)
4. **Customize branding** and styling
5. **Add e-signature integration** (DocuSign, HelloSign, etc.)

## 💡 Tips

- **Test with fake data first** before using with clients
- **Keep a backup** of your GitHub repository
- **Document your changes** in commit messages
- **Use Vercel preview deployments** to test before going live

## 📞 Support

For issues with:
- **Vercel deployment:** https://vercel.com/docs
- **Python-docx:** https://python-docx.readthedocs.io/
- **GitHub:** https://docs.github.com/

- ## Template Management
   
   Templates are stored in Google Drive for easy editing by legal staff.
   
   - **Edit templates**: Open files in Google Drive
   - **Changes go live**: Immediately on save
   - **Version history**: Available in Google Drive
   
   See `docs/GOOGLE_DRIVE_SETUP.md` for details.

## 📄 License

This project is private and proprietary to Muletown Law, P.C.

---

**Ready to deploy? Follow the steps above!** 🚀
