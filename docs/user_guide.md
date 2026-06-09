# ItsStoryDay - User & Administrator Guide

This guide provides exhaustive instructions for setting up, configuring, customising, and troubleshooting the ItsStoryDay Automation Platform.

---

## 🧭 Setup & Installation Guide

The platform is designed to be highly portable, relying solely on standard Python libraries and standard API integrations.

### Local Installation
1. Install Python 3.12+ from official sources.
2. Clone this repository locally.
3. Install standard requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run locally to test:
   ```bash
   python main.py
   ```

---

## 📧 Email Configuration & SMTP Setup

The default configuration is configured for **Gmail**.

### Using Gmail
To use a Gmail address as the sender:
1. Ensure your Google account has **2-Step Verification** turned on.
2. Go to your Google Account Settings > **Security**.
3. Under *How you sign in to Google*, select **2-Step Verification**.
4. Scroll to the bottom and select **App passwords**.
5. Generate an app-specific password (select App = "Other" and name it e.g. "ItsStoryDay").
6. Copy the generated 16-character code (e.g. `xrnr zfir nhfr zwpl`) and use it as `SMTP_PASSWORD` in your `.env` or GitHub Secrets.

### Using Other SMTP Providers
You can configure other SMTP services like SendGrid, Mailgun, or standard webmail:
- Update `SMTP_SERVER` and `SMTP_PORT` in your `.env` or the GitHub Action Environment block.
- Examples:
  - **SendGrid:** Server: `smtp.sendgrid.net`, Port: `587`, Username: `apikey`, Password: `<your_sendgrid_api_key>`
  - **Mailgun:** Server: `smtp.mailgun.org`, Port: `587`, Username: `<postmaster@yourdomain.com>`, Password: `<password>`

---

## 🤖 AI API Configuration (Groq)

The application uses Groq's high-speed inference engine. You can change models by editing the `GROQ_MODEL` variable.

### Supported Models
By default, the code uses `llama-3-70b-8192` or `llama-3.3-70b-specdec`.
- `llama-3.3-70b-specdec`: Extremely high reasoning capabilities, excellent for rich dialogue, character depth, and complex storytelling structure. Highly recommended.
- `llama-3.1-70b-versatile`: Versatile and stable model.
- `llama-3-70b-8192`: Standard, reliable high-performance model.

---

## 🛠️ Customisation & Extension

### Modifying the Categories List
To change or add story categories:
1. Open [generator.py](file:///d:/Dev_Projects/Blogpost_Auto/src/story/generator.py).
2. Locate the global list `CATEGORIES` and add/edit entries.
3. Update the category guidelines in `prompts/topic_generator.txt` to give clear instructions to the AI on the new categories.

### Adjusting Word Limits
The AI client enforces Pydantic validations on story length. If you want to increase or decrease the target size:
1. Update `BLOG_LENGTH_MIN` and `BLOG_LENGTH_MAX` in your configuration (`.env` or GitHub Secrets).
2. Update the `validate_word_count` logic in [models.py](file:///d:/Dev_Projects/Blogpost_Auto/src/story/models.py#L60-L68) to match the new minimum limits.

---

## 🔍 Troubleshooting Guide

### 1. SMTP/Email Errors
* **Error:** `SMTPAuthenticationError: Username and Password not accepted`
  * **Solution:** If using Gmail, make sure you are using a 16-character **App Password** (not your main Google account password) and that 2-Step Verification is active on the account.
* **Error:** `Connection timed out` or `ConnectionRefusedError`
  * **Solution:** Verify the `SMTP_PORT` is set correctly. Standard ports are `587` (STARTTLS) and `465` (SSL). Ensure your firewall or network allows traffic on these ports.

### 2. GitHub Actions Write Permissions Failures
* **Error:** `fatal: unable to access ...: Permission to ... denied to github-actions[bot]`
  * **Solution:** GitHub repository Action permissions default to Read-Only. You must navigate to **Settings** > **Actions** > **General** > **Workflow permissions** in your repository page and toggle **Read and write permissions**.

### 3. Pydantic validation errors (JSON schema mismatch)
* **Error:** `StoryResponse: related_keywords: must contain exactly 15 elements`
  * **Solution:** The Groq client has built-in exponential backoff retries. If the LLM generates 14 keywords instead of 15, the client will automatically catch the error, re-instantiate, and fetch a valid structure. If errors persist, try changing the model in `.env` to `llama-3.3-70b-specdec` for better instruction following.

### 4. Pexels Image API returns empty
* **Error:** `No photos found for query`
  * **Solution:** Pexels API will fall back automatically to broader queries like the category name (e.g. "Mystery Stories" -> searching Pexels for "mystery") if specific visual keyword terms fail. Ensure your `PEXELS_API_KEY` is set correctly.
