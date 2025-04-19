# Excel Backend

This document provides instructions for setting up and running the Excel backend.

## Setup Instructions

### Option 1: Local Setup

1. Setup the environment by copying the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Install Playwright and its dependencies:

   ```bash
   pip install playwright
   playwright install-deps chromium
   ```

3. Install Poetry (dependency management):

   ```bash
   pip install poetry
   ```

4. Install project dependencies:

   ```bash
   poetry install
   ```

5. Run the development server:
   ```bash
   poetry run dev
   ```

### Option 2: Docker Setup

Simply run:

```bash
docker compose up
```
