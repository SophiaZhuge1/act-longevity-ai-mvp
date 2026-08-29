# ACT Longevity AI MVP

Early implementation of the 70-90 focused elderly wellness web app.

## What Is Included

- Python backend using the standard library HTTP server.
- React single-page app powered by Vite.
- Questionnaire based on the current ACT wellness check plus added sleep and nutrition questions.
- 8-category health dashboard radar plot.
- Health persona and practical recommendation generation.
- Local resource and YouTube search suggestions.
- MongoDB-compatible vector document storage with local JSON fallback.

## Run Locally

Install frontend packages:

```bash
npm install
```

Start the backend:

```bash
npm run backend
```

In a second terminal, start the React app:

```bash
npm run dev
```

Open the local URL shown by Vite, usually:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/api` requests to the Python backend on port `8000`.

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
```

The backend will write to these collections:

- `users`
- `vector_documents`
- `chat`

The current embeddings are deterministic local mock embeddings. For production, replace them with OpenAI embeddings or MongoDB Atlas Vector Search embeddings.

## Future API Details Needed

No paid API keys are required for the current mock MVP.

When ready, add:

- `OPENAI_API_KEY` for real persona/recommendation generation and embeddings.
- A local search provider key such as Google Places, SerpAPI, or Bing Search for postcode-based services.
- MongoDB Atlas connection string for hosted database and vector search.

## Backend Endpoints

- `GET /api/questions`
- `POST /api/assessments`
- `GET /api/users`
- `GET /api/users/{user_id}`
- `GET /api/local-resources?user_id=...`
- `POST /api/chat`
