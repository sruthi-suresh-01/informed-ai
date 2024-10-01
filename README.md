# Informed AI

## Overview

Informed AI is designed to help users get personalized updates about the weather in their location

## Code Setup

### Initial Setup

1. **Fork the Repository**: Start by forking the repo to your GitHub account.
2. **Clone and Navigate**: Clone the forked repository to your local machine and navigate to the root folder of the project.

   ```bash
   git git@github.com:rahulrajesh23/informed-ai.git project_name
   cd project_name
   ```
3. **~~Install Redis~~**:
  - This step is no longer required. Please uninstall Redis if it is installed.

4. **Environment Setup**:
   - Install Poetry
   - Run `make install`
   - Navigate to `frontend` directory and run `npm install`
5. **Create .env file**:
   - Rename the `.env.template` file in the root directory and configure your API Key and other environment variables
   - Note: As of now, only `GPT_APIKEY` and `GPT_MODEL_NAME` needs to be specified

## Running the server

### For Development

In the root directory, run `python main_dev.py`
