# Whispering Integration Strategy
Version: 1.0
Timestamp: 2025-07-27 00:15 CET

## 1. Executive Summary

This document outlines the strategic plan to integrate our advanced `whisper_client` (Python-based WebSocket streaming client for WhisperLive) with the "Whispering" desktop application. The goal is to combine our powerful, low-latency transcription engine with Whispering's excellent, cross-platform user interface.

After a thorough analysis of the "Whispering" codebase, a direct Pull Request (PR) of our Python logic is not feasible due to a technology mismatch (Python vs. TypeScript/Rust). A complete rewrite of our logic in TypeScript would be a high-effort, high-risk endeavor.

Therefore, we will pursue a **strategic, two-stage integration approach**:

*   **Stage 1: OpenAI-Compatible API (Proof of Concept)**: We will add an API server mode to our Python client that perfectly mimics the OpenAI Whisper API. This allows for a minimal, low-risk PR to "Whispering" that adds our client as a new "local" backend, following the exact pattern used by their existing "Speaches" integration. This provides immediate value and builds a collaborative foundation.
*   **Stage 2: True Streaming Integration (Evolution)**: After successfully establishing a presence in the "Whispering" ecosystem, we will propose a more advanced integration that exposes our true streaming capabilities to the UI, enabling real-time transcription feedback.

This approach minimizes initial risk, delivers immediate value, and creates a strategic path toward a "best-of-both-worlds" solution.

## 2. Analysis of the "Whispering" Repository

### Key Findings:
*   **Tech Stack**: A modern monorepo using Svelte 5, Tauri (with Rust), TypeScript, and Bun. The architecture is clean and well-documented.
*   **Core Architecture**: A three-layer system (UI -> Query -> Service) that separates concerns effectively.
*   **Backend Integration Pattern**: New backends are added as "Services". The existing integrations for cloud services (OpenAI, Groq) and local services ("Speaches") are all based on a stateless, request-response HTTP paradigm. They expect to send a full audio `Blob` and receive a complete text transcription.
*   **The "Speaches.ts" Blueprint**: The integration of the "Speaches" local server is the key to our strategy.
    *   "Whispering" does **not** start or manage the Speaches process.
    *   It acts as a simple HTTP client to a user-configured base URL (e.g., `http://localhost:8080`).
    *   The API endpoint it calls (`/v1/audio/transcriptions`) is designed to be **OpenAI-compatible**.
    *   This proves that "Whispering" has an established, accepted pattern for integrating with external, user-managed local servers via a standardized API.

### Conclusion for Integration:
A direct port of our streaming logic is complex and invasive. The path of least resistance and highest acceptance probability is to make our `whisper_client` **look like another "Speaches"** from Whispering's perspective.

## 3. The Two-Stage Integration Plan

### Stage 1: The OpenAI-Compatible API Server (PoC & Entry Point)

**Objective**: Achieve a fast, simple, and successful initial integration.

#### Task 1: Enhance `whisper_client` with an API Server Mode
We will add a new operational mode to our `main.py`.

*   **Technology**: Use `FastAPI` and `uvicorn` for a lightweight, high-performance web server.
*   **Command**: `python main.py serve --host 0.0.0.0 --port 8000`
*   **Endpoint**: Implement `POST /v1/audio/transcriptions`.
    *   **Request**: The endpoint will accept `multipart/form-data`, identical to the OpenAI API, expecting a `file` field containing the audio.
    *   **Internal Logic**: Upon receiving a request, the server will:
        1.  Take the complete audio data from the request.
        2.  Invoke our existing WebSocket client logic to connect to the WhisperLive container.
        3.  Stream the audio data internally.
        4.  Wait for the final, consolidated transcription result from our text processing engine.
        5.  Format the result into an OpenAI-compatible JSON response: `{"text": "The transcribed text..."}`.
    *   **Result**: From the outside, our client behaves like a simple, stateless API, while internally it leverages our powerful streaming engine for fast processing.

#### Task 2: Prepare the Minimal PR for "Whispering"
We will create a new file, `whisperlive.ts`, in the "Whispering" services directory.

*   **Implementation**: This file will be a near-copy of `speaches.ts`.
*   **Functionality**: It will construct a `FormData` object and make an HTTP POST request to the user-configured `baseUrl` for our client's API server.
*   **Configuration**: We will add the necessary UI elements in the settings for the user to enable the "WhisperLive (via local client)" backend and set the server URL.

### Stage 2: The True Streaming API (The Ultimate Goal)

**Objective**: Expose our core streaming advantage to the user via the "Whispering" UI.

*   **Prerequisite**: Successful integration and acceptance of Stage 1.
*   **Approach**:
    1.  **Propose an Enhancement**: Open a new GitHub issue or discussion with Braden Wong.
    2.  **Suggest a new Backend-Type**: Propose a new "streaming" adapter type alongside the existing request-response type.
    3.  **Technical Implementation**:
        *   Our Python client would expose a WebSocket endpoint (e.g., `/v1/audio/stream`).
        *   The new "Whispering" adapter would establish a WebSocket connection to this endpoint.
        *   Audio chunks would be sent from the UI to our server.
        *   Transcription segments would be sent back from our server to the UI in real-time to be displayed as they arrive.
*   **Collaboration**: This stage would be approached as a collaborative effort with the "Whispering" maintainer, building on the foundation and trust established in Stage 1.

## 4. Deployment & Setup Strategy for End-Users

To ensure a simple and reliable setup for the end-user, we will package our solution using Docker Compose. This approach avoids a complex manual setup of starting two separate server processes (the WhisperLive container and our client's API server).

### The Docker Compose Approach

Docker Compose is the industry-standard tool for defining and running multi-container Docker applications. It allows us to define our entire application stack in a single, declarative `docker-compose.yml` file.

**Advantages:**
*   **Simplicity for the User**: The user only needs to run one command (`docker-compose up`) to start the entire system.
*   **Robustness**: Docker Compose handles the networking between containers, startup order, and process management.
*   **Declarative & Maintainable**: The `docker-compose.yml` file is easy to read, understand, and maintain.

### Application Components

Our stack will consist of two services:

1.  **The WhisperLive Server (The "Engine")**: We will use the official, pre-built Docker image for WhisperLive without modification.
2.  **Our Client (The "API Bridge")**: We will create a simple Docker image for our own Python client. This image will contain our code and all its dependencies.

### `Dockerfile` for Our Client

Creating the image for our client is straightforward. We will add a `Dockerfile` to our project root with the following content:

```dockerfile
# 1. Use an official, slim Python image as a base
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy our application code into the container
COPY . .

# 5. Define the default command to run when the container starts
CMD ["python", "main.py", "serve", "--host", "0.0.0.0"]
```

### `docker-compose.yml` Structure

The `docker-compose.yml` file will define both services and connect them.

```yaml
version: '3.8'

services:
  # Service 1: The WhisperLive transcription engine
  whisper-live:
    image: whisper-live-image:latest # Placeholder for the actual image name
    # ... (ports, volumes, and other necessary configurations)

  # Service 2: Our client, acting as the API bridge
  whisper-client-bridge:
    build: . # Tells Docker Compose to build the image from the Dockerfile in the current directory
    ports:
      - "8000:8000" # Exposes our API server to the host machine
    depends_on:
      - whisper-live # Ensures the engine starts before our bridge
```

This setup provides a professional, one-command-start experience for the user.

## 5. Immediate Next Steps (Action Plan)

1.  **Confirm Plan**: User has confirmed the strategy.
2.  **Switch to ACT_MODE**.
3.  **Create `Dockerfile`**: Add the `Dockerfile` as specified above to the project root.
4.  **Create `docker-compose.yml`**: Add the `docker-compose.yml` file.
5.  **Modify `requirements.txt`**: Add `fastapi`, `uvicorn`, and `docker` as new dependencies.
6.  **Create `src/api_server.py`**: Begin implementation of the FastAPI server logic.
7.  **Update `main.py`**: Add the new `serve` command and integrate the "WhisperLive-Manager" logic to auto-start the Docker Compose setup if not running.
