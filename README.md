# ACT Longevity AI MVP

Early implementation of the ACT Assess free taster and Healthy Longevity report.

## What Is Included

- Python backend using the standard library HTTP server.
- React single-page app powered by Vite.
- Senior-friendly ACT wellness check with 26 first-line questions and conditional follow-ups for falls, accommodation, finances and mood.
- A prioritisation step where each person chooses up to three flagged concerns to put at the centre of their plan.
- Personal profile capture for date of birth, contact details, postcode, home life, care support and employment background.
- 5-dimension Healthy Longevity spider-gram covering Staying Healthy, Independence, Wellbeing, Social Resources and Clinical Risk.
- Summary report ordered by significant clinical risks, the person's chosen priorities, prevention opportunities and other practical support.
- Consent capture, waitlist capture and anonymised population analytics storage.
- PDF report generation and optional email delivery when SMTP is configured.
- Health persona and practical recommendation generation for the later premium AI support flow.
- Postcode-aware local resources plus dedicated gentle movement and healthy recipe video sections.
- Friendly text-to-speech summary and profile-grounded Ask ACT AI follow-up chat (requires an OpenAI API key).
- Private longitudinal progress records, repeat assessments and five-score trend dashboard.
- MongoDB-compatible vector document storage with local JSON fallback.

## Run Locally In Terminal

Open Terminal and move into the app folder:

```bash
cd /Users/zhuge/Documents/stockroom/longevity-app
```

Install the app packages. You only need to do this the first time, or after dependencies change:

```bash
npm install
npm run setup:backend
```

Start the full local app:

```bash
npm run start
```

This starts both parts of the MVP:

- React frontend: `http://127.0.0.1:5173`
- Python backend API: `http://127.0.0.1:8000`

Open this in your browser:

```text
http://127.0.0.1:5173
```

Keep the Terminal window open while testing. To stop the app, press:

```text
Control + C
```

## Run Frontend And Backend Separately

If you prefer to see each part in its own Terminal window, use this method instead.

In Terminal window 1:

```bash
npm install
npm run setup:backend
npm run backend
```

In Terminal window 2:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` requests to the Python backend on port `8000`.

## Quick Health Check

After starting the app, you can check the backend is awake by opening:

```text
http://127.0.0.1:8000/api/health
```

You should see:

```json
{"ok": true}
```

## MongoDB Vector Store

The backend works without MongoDB by saving to:

```text
backend/data/local_store.json
```

To use MongoDB, install the Python driver:

```bash
python3 -m pip install pymongo
```

Then set:

```bash
export MONGODB_URI="mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority"
export MONGODB_DB="longevity_app"
npm run start
```

Replace `USER`, `PASSWORD`, and `CLUSTER` with your MongoDB Atlas details.

The backend will write to these collections:

- `members`
- `users`
- `vector_documents`
- `chat`
- `waitlist`
- `population_analytics`

The current embeddings are deterministic local mock embeddings. Ask ACT uses the current user's structured assessment and recommendations, not a cross-user vector search. For production, replace the mock embeddings with a reviewed embedding and search design.

## Longitudinal Progress

The first assessment for an email address creates a private member record and an access code such as `ACT-ABCD-2345`. The code appears on the results screen and is included in the report email when SMTP succeeds. It is stored only as a hash.

A returning person signs in with the same email and access code. Each repeat assessment is saved as a separate immutable record linked to the member ID. The progress dashboard shows:

- all five scores across assessment dates;
- the change since the previous assessment;
- a dated list of past assessments, summaries and chosen priorities.

Existing records created before this feature are not automatically claimed because email-only matching would expose private health history. Those users begin a new longitudinal record the next time they complete an assessment. The MVP applies basic per-instance limits to sign-in attempts and Ask ACT requests. Before a wider public launch, add a reviewed account-recovery flow, durable rate limiting, audit logs and a formal retention policy.

## Ask ACT AI

The chat uses the assessment answers, five scores, chosen priorities, clinical flags and ACT recommendations to answer follow-up questions. A person must opt in within the chat before their assessment context is sent to OpenAI. Direct identifiers such as name, full postcode, phone number and date of birth are not sent. The provider request sets `store: false`; ACT stores the conversation locally or in MongoDB so follow-up questions retain context.

Add these values to the local `.env` file, then restart the app:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-5-mini
ACT_ADMIN_API_KEY=a_long_random_admin_secret
```

Without an OpenAI key, the assessment still works, but Ask ACT clearly shows that AI is unavailable. The key belongs only on the backend; never put it in a `VITE_` variable or commit `.env`. The `GET /api/users` routes require the `X-Admin-Key` header matching `ACT_ADMIN_API_KEY`. Older assessments need to be retaken to receive a chat access token.

This is a wellness guide, not a diagnostic or emergency service. Clinical review, access control, privacy assessment, retention rules and evaluation with representative older adults are needed before public release.

## Emailing PDF Reports

The app creates a PDF report after each completed taster assessment. To email the PDF to the user, configure SMTP before starting the backend:

Create a local `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and add your real SMTP details:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourgmail@gmail.com
SMTP_PASSWORD=your_16_character_app_password
SMTP_FROM=ACT <yourgmail@gmail.com>
SMTP_USE_TLS=true
```

Start the app:

```bash
npm run start
```

For testing, you can use an SMTP provider such as SendGrid, Mailgun, Postmark, Brevo, or a Gmail app password. Do not commit SMTP passwords to GitHub.

If SMTP is not configured, the app still creates the PDF locally in:

```text
backend/data/reports/
```

The report page will show whether the email was sent or whether SMTP still needs to be configured.

## Deploy To Render

The repository includes `render.yaml`, which builds the React app and serves it with the Python backend as one free Render web service.

1. Push the current branch to GitHub.
2. In MongoDB Atlas, create a database user and copy the `mongodb+srv://...` application connection string. Add network access for Render. Free Render services do not have a fixed outbound IP, so a test setup may need `0.0.0.0/0`; use a strong database password and restrict this for production.
3. In Render, choose **New > Blueprint**, connect this repository and approve the service.
4. Enter the prompted secret values: `MONGODB_URI`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, and `OPENAI_API_KEY`.
5. Wait for `/api/health` to report `{"ok": true, "database": "mongodb"}`.

The hosted service requires MongoDB and will stop during startup if the database is unavailable, preventing health records from silently being written to Render's temporary filesystem. SMTP and OpenAI can be left blank for an initial assessment-only test, but reports will not be emailed and Ask ACT will remain unavailable.

Render's free service may sleep while idle, so the first visit after a period of inactivity can take longer. It is suitable for testing, not a clinical production launch.

## Common Local Issues

If `npm run start` says a port is already in use, an older local copy may still be running. Stop the old Terminal process with `Control + C`, then run `npm run start` again.

If the dashboard button does not respond, check that the backend is running by visiting:

```text
http://127.0.0.1:8000/api/health
```

If you see `{"ok": true}`, refresh the frontend page and try again.

## Future API Details Needed

No paid API key is needed to complete the assessment. Ask ACT AI requires an OpenAI API key.

When ready, add:

- `OPENAI_API_KEY` for Ask ACT's profile-grounded follow-up answers. The assessment report and mock embeddings remain deterministic.
- A local search provider key such as Google Places, SerpAPI, or Bing Search for postcode-based services.
- MongoDB Atlas connection string for hosted database and vector search.
- SMTP credentials for PDF report and waitlist email delivery.

## Backend Endpoints

- `GET /api/questions`
- `POST /api/assessments`
- `POST /api/members/login`
- `GET /api/users`
- `GET /api/users/{user_id}`
- `GET /api/local-resources?user_id=...`
- `POST /api/chat`
- `GET /api/chat/status`
