# Deployment & Evaluation Guide for MedGraph AI (Auth Backend)

Welcome to the MedGraph AI authentication backend! This guide will help judges, evaluators, and developers quickly spin up the authentication server locally.

We use **Google OAuth 2.0** for seamless sign-in, and this backend is built purely in **TypeScript** using **Express**.

---

## 🚀 1. Prerequisites

Before starting, ensure you have the following installed on your machine:
- **Node.js** (v18 or higher recommended)
- **npm** (comes with Node.js)

---

## ⚙️ 2. Environment Setup

For security reasons, we do not commit our live Google API keys (the `.env` file) to the repository. 
You must create a `.env` file using the provided template.

1. In the root of the project, locate the file named `.env.example`.
2. Duplicate or rename `.env.example` to exactly **`.env`**.
3. Open `.env` and fill in the missing variable values provided by our team:
   ```env
   GOOGLE_CLIENT_ID="[Paste the 566859303240... string here]"
   GOOGLE_CLIENT_SECRET="[Paste the GOCSPX... string here]"
   GOOGLE_REDIRECT_URI="http://localhost:3000/oauth2callback"
   PORT=3000
   ```
*(Note for evaluators: Please request the active Google Client ID and Secret from the team if they were not provided in your submission packet.)*

---

## 📦 3. Installation

Once your `.env` is configured, install the required dependencies:

```bash
npm install
```
This will install Express, TypeScript execution tools, and necessary session/cookie managers.

---

## 🏃 4. Running the Server

Start the local backend server with:

```bash
npx tsx server.ts
```

If successful, your console will output:
> `Server is running at http://localhost:3000`

---

## 🧪 5. Testing the Auth Flow

1. Open a browser and navigate to **[http://localhost:3000](http://localhost:3000)**.
2. You will see the public homepage indicating you are not logged in.
3. Click **"Login with Google"**.
4. Authenticate using your Google account.
5. You will naturally be redirected to `http://localhost:3000/oauth2callback`, where the backend silently exchanges the tokens, verifies CSRF state security, sets an HTTP-only secure cookie, and directs you to `/dashboard`.
6. On the **Dashboard**, you will see your Google Profile Information alongside a button to test the **Protected API Endpoint** (`/api/secure-health-data`).

---

## 🛠️ Architecture Notes for Judges
- **No Database Needed**: For hackathon velocity, sessions are tracked via a fast in-memory `Map` linked to securely generated `UUID` cookies via `session_manager.ts`.
- **Strict Typing**: The entire OAuth lifecycle (`config`, `token validation`, `error handling`, `routing`) is built in strict TypeScript.
- **Graceful Failure**: See `error_handler.ts`—auth failures cleanly log and wipe sessions to prevent app-breaking redirect loops.
