# Free Hosted Test Deployment

Recommended testing setup: **Render Free Web Service + MongoDB Atlas Free Cluster**.

GitHub Pages is not suitable for the full version because it cannot run the Python backend. This app is now packaged so the Python backend serves both:

- the React frontend from `dist/`
- the API under `/api/...`

The React app calls the backend with same-origin `/api` URLs, so no public API base URL is needed for this one-service deployment.

## 1. Push This Folder To GitHub

Create a new GitHub repository, for example:

```text
act-longevity-ai-mvp
```

Push the contents of this `longevity-app` folder to that repo.

Do not commit:

- `node_modules/`
- `backend/data/local_store.json`
- `.env`

## 2. Create A Free MongoDB Atlas Cluster

1. Go to https://www.mongodb.com/products/platform/atlas-database
2. Create a free cluster.
3. Create a database user and password.
4. Allow network access from `0.0.0.0/0` for testing.
5. Copy the connection string.

It will look like:

```text
mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

## 3. Deploy On Render

1. Go to https://render.com/
2. Create a free account.
3. Click `New` -> `Blueprint`.
4. Connect your GitHub repo.
5. Render will read `render.yaml`.
6. Add this environment variable when prompted:

```text
MONGODB_URI=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

The app will use:

```text
MONGODB_DB=longevity_app
```

## 4. What Render Will Run

Build:

```bash
npm install && npm run build && python3 -m pip install -r backend/requirements.txt
```

Start:

```bash
python3 backend/app.py
```

## 5. Free-Tier Notes

Render free web services can sleep after being idle, so the first visit may take around a minute to wake up.

Local file storage on free web services is temporary. That is why MongoDB Atlas should be used for the vector/user data.

## 6. Current API Keys

No OpenAI API key is required for the mock MVP.

Later production upgrades:

- `OPENAI_API_KEY` for real LLM recommendations and embeddings.
- Google Places, SerpAPI, or Bing Search API key for real postcode-based local resources.
