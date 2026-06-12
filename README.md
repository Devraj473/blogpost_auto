# ItsStoryDay - AI Story Blog Automation Platform

ItsStoryDay is a production-ready, serverless Python automation platform that automatically generates high-quality AI-focused educational blog posts every day, stores them in structured folders in this GitHub repository, and emails the complete post to a configured email address.

The platform is designed to run automatically through **GitHub Actions** daily at **9:00 AM IST (3:30 AM UTC)**, requiring no VPS, server, or local machine.

---

## 🌟 Key Features

- **Practical AI Educational Writing:** Integrates the Groq API (using highly advanced LLM models like `llama-3.3-70b-specdec` or `llama-3-70b-8192`) to craft practical AI-focused educational content (1500–3000 words).
- **Free Visual Assets:** Automatically queries the Pexels (Pixel) API to fetch and download high-quality stock photo URLs relevant to the daily AI topic's visual focus, automatically embedding them in the email and HTML posts.
- **Sequential Category Rotation:** Tracks category selections in a local state file (`config/state.json`) which is updated and pushed back to the Git repository, guaranteeing that 10 AI-focused categories rotate sequentially "line-by-line".
- **Dynamic SEO Optimization:** Automatically builds complete SEO title, meta description, primary keyword, 15 related keywords, 15 SEO tags, and URL slug.
- **Beautiful HTML Newsletter Emails:** Dispatches premium styled responsive HTML emails through SMTP with embedded visuals, serif reading layouts, styled blockquotes, and Q&A accordions.
- **Organized Storage:** Writes generated posts inside `blogs/YYYY/MM/DD/` directories as `story.md`, `story.html`, `metadata.json`, and `image_prompt.txt`.

---

## 📂 Project Structure

```
itsstoryday-automation/
├── .github/workflows/
│   └── daily_story.yml        # GitHub Actions Scheduler (Daily 9:00 AM IST)
├── src/
│   ├── ai/
│   │   ├── base.py            # Abstract Base AI client
│   │   └── groq_client.py     # Groq API Client wrapper with JSON enforcement & retries
│   ├── email_sender/
│   │   └── smtp_sender.py     # SMTP Email sender module (STARTTLS & SSL)
│   ├── image/
│   │   └── pexels_client.py   # Pexels stock photo search client
│   ├── storage/
│   │   └── file_storage.py    # Local file writing (markdown, metadata, rendered html)
│   ├── story/
│   │   ├── generator.py       # Topic generation & category state router
│   │   ├── models.py          # Pydantic validation schemas
│   │   └── prompts.py         # Prompt loader utility
│   ├── config.py              # Configuration manager
│   └── logger.py              # central rolling file logger setup
├── config/
│   └── state.json             # tracks category sequential indexes across commits
├── prompts/
│   ├── topic_generator.txt    # prompt template for AI topic selection
│   └── story_generator.txt    # prompt template for AI content writing
├── templates/
│   └── email_template.html    # responsive Jinja2 HTML email template
├── tests/
│   ├── test_generator.py      # generator validation unit tests
│   └── test_email.py          # SMTP diagnostic utility script
├── requirements.txt           # Python application dependencies
├── .env                       # Local environment variables (Pre-configured!)
├── .env.example               # Reference template for environment variables
└── main.py                    # Orchestrator Entrypoint
```

---

## ⚙️ Local Setup and Installation

### 1. Prerequisites
- Python 3.12 or higher installed on your system.
- Git.

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd itsstoryday-automation
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration (`.env`)
The workspace includes a `.env` file pre-filled with your credentials:
```ini
GROQ_API_KEY=gsk_RFKeeoamEt6rRx...
PEXELS_API_KEY=SwcJUIMVnh9jqzf...
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=dc4682786@gmail.com
SMTP_PASSWORD="xrnr zfir nhfr zwpl"
RECIPIENT_EMAIL=dc4682786@gmail.com
```

### 5. Running it Locally
You can run the script manually:
```bash
python main.py
```
This will:
1. Load credentials.
2. Select the next AI-focused category sequentially from `config/state.json`.
3. Check recently written topics in `blogs/` to avoid duplication.
4. Generate the daily AI topic and long-form content using Groq.
5. Search Pexels for a visual asset.
6. Create files in `blogs/YYYY/MM/DD/`.
7. Deliver the daily AI content email.
8. Save the state back to `config/state.json`.

---

## 🤖 GitHub Actions Setup (Zero-Server Deployment)

To configure this to run automatically every day at 9:00 AM IST (3:30 AM UTC):

### Step 1: Push your project to GitHub
Create a private (or public) GitHub repository and push this codebase:
```bash
git init
git add .
git commit -m "Initialize ItsStoryDay automation platform"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Configure Repository Secrets
In your GitHub repository web interface:
1. Go to **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret** and add the following 5 secrets:
   - `GROQ_API_KEY`: `your_groq_api_key_here`
   - `PEXELS_API_KEY`: `your_pexels_api_key_here`
   - `SMTP_EMAIL`: `your_smtp_sender_email_here`
   - `SMTP_PASSWORD`: `your_email_app_password_here`
   - `RECIPIENT_EMAIL`: `your_recipient_email_here`

### Step 3: Enable Action Permissions
To allow GitHub Actions to commit the generated blog files and the updated `state.json` file back to the repository:
1. Go to **Settings** > **Actions** > **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Click **Save**.

Now the script will run automatically every morning, generate files, email them, commit the daily blog folder to your GitHub repo, and advance the category index for the next day.
You can also trigger it manually anytime by going to the **Actions** tab in GitHub, clicking **Daily AI Content Automation**, and selecting **Run workflow**.
