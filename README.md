# ACT Longevity AI MVP

Early implementation of the ACT Assess free taster and Healthy Longevity report.

## What Is Included

- Python backend using the standard library HTTP server.
- React single-page app powered by Vite.
- Questionnaire based on the current ACT wellness check plus added sleep and nutrition questions.
- 5-dimension Healthy Longevity spider-gram.
- Summary report with priorities for support, prevention opportunities and clinical risks to discuss.
- Consent capture, waitlist capture and anonymised population analytics storage.
- PDF report generation and optional email delivery when SMTP is configured.
- Health persona and practical recommendation generation for the later premium AI support flow.
- Local resource and YouTube search suggestions.
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

- `users`
- `vector_documents`
- `chat`
- `waitlist`
- `population_analytics`

The current embeddings are deterministic local mock embeddings. For production, replace them with OpenAI embeddings or MongoDB Atlas Vector Search embeddings.

## Emailing PDF Reports

The app creates a PDF report after each completed taster assessment. To email the PDF to the user, configure SMTP before starting the backend:

```bash
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_smtp_username"
export SMTP_PASSWORD="your_smtp_password"
export SMTP_FROM="ACT <hello@actnow.health>"
export SMTP_USE_TLS="true"
npm run start
```

For testing, you can use an SMTP provider such as SendGrid, Mailgun, Postmark, Brevo, or a Gmail app password. Do not commit SMTP passwords to GitHub.

If SMTP is not configured, the app still creates the PDF locally in:

```text
backend/data/reports/
```

The report page will show whether the email was sent or whether SMTP still needs to be configured.

## Common Local Issues

If `npm run start` says a port is already in use, an older local copy may still be running. Stop the old Terminal process with `Control + C`, then run `npm run start` again.

If the dashboard button does not respond, check that the backend is running by visiting:

```text
http://127.0.0.1:8000/api/health
```

If you see `{"ok": true}`, refresh the frontend page and try again.

## Future API Details Needed

No paid API keys are required for the current mock MVP.

When ready, add:

- `OPENAI_API_KEY` for real persona/recommendation generation and embeddings.
- A local search provider key such as Google Places, SerpAPI, or Bing Search for postcode-based services.
- MongoDB Atlas connection string for hosted database and vector search.
- SMTP credentials for PDF report and waitlist email delivery.

## Backend Endpoints

- `GET /api/questions`
- `POST /api/assessments`
- `GET /api/users`
- `GET /api/users/{user_id}`
- `GET /api/local-resources?user_id=...`
- `POST /api/chat`
