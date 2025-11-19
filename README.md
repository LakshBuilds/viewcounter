# Instagram Reel Intelligence Dashboard

This Streamlit dashboard lets you paste an Instagram reel URL (or username) and instantly explore the media and engagement metadata returned by the Apify Instagram Reels actor (`xMc5Ga1oCONPmWJIa`).

## Prerequisites

- Python 3.10+
- An Apify API token (the sample token from the request is prefilled in the UI; prefer your own token for production).

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The dashboard launches on `http://localhost:8501`.

## Using the dashboard

1. Paste your Apify API token in the configuration accordion (or set `APIFY_API_TOKEN` in the environment before launching the app).
2. Choose how many results you want to fetch.
3. Enter a reel URL such as `https://www.instagram.com/reel/...` (usernames without the `@` symbol also work).
4. Click **Fetch reel data**.

For each reel returned, you will see:

- **Reel Overview** – identifiers, owner handle, caption.
- **Engagement** – likes, comments, views, saves, shares (when present).
- **Media** – thumbnails, video URLs, audio metadata.
- **Timing** – timestamps exposed by the API.
- **Raw Payload** – the unedited JSON from Apify for debugging or downstream uses.

## Environment variables

| Name              | Description                                    |
| ----------------- | ---------------------------------------------- |
| `APIFY_API_TOKEN` | Optional. Pre-populates the token input field. |

## Development notes

- The Apify client is cached per token to reduce repeated authentications.
- Section headings render only when the corresponding fields exist in the payload, so the layout adapts to whatever the API returns.



