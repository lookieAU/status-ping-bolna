# Bolna LLM Status Tracker

A lightweight webhook-based service for receiving and tracking status events from a Bolna LLM agent.

## Overview

This FastAPI app tracks LLM provider status updates via two approaches that work in tandem:

- **Webhook** — listens for incoming status events pushed from a Slack integration to the `/status-event` endpoint.
- **RSS polling** — periodically polls LLM provider status page RSS feeds, parses new entries, and stores them alongside webhook events.

## Endpoints

- `GET /` — Health check
- `POST /status-event` — Receive a status event webhook
- `GET /api/status/all` — Retrieve all recorded status events

## Setup

```bash
pip install -r requirements.txt
python main.py
```

The server starts on `http://0.0.0.0:8000`.

## Project Structure

```
.
├── main.py               # App entry point
├── api/
│   ├── challenge.py      # Webhook receiver route
│   └── status.py         # Status query route
├── models/
│   └── challenge.py      # Request/response models
├── services/
│   ├── challenge.py      # Webhook event handling logic
│   ├── rss_monitor.py    # RSS feed poller and parser
│   └── status.py         # Status retrieval logic
└── repository/
    └── db_mock.py        # In-memory data store
```

## Scalability

New providers can be easily added. We have to just subscribe the events from the status tracker to the designated slack channel which will subsequently publish the event to our webhook endpoint.

For the RSS approach, we just need to add the polling URLs to the DB.