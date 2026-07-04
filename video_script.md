# Kavalar: Video Presentation & Walkthrough Script

This script outlines a **5-8 minute voiceover and step-by-step action plan** for presenting the Kavalar AI Governance and Behavioral Anomaly Detection platform. Use this as a guide to narrate your screencast.

---

## 🎬 Section 1: Introduction & High-Level Overview (0:00 - 0:45)

### Visuals
- Show the Kavalar Governance Dashboard home page (running on `http://localhost:3000`).
- Hover over the active baseline status and anomaly statistics counts.

### Voiceover
> "Hello and welcome. In this video, I will demonstrate **Kavalar**, an enterprise-grade AI security governance platform designed to protect LLM agents from **indirect prompt injection attacks**.
> 
> As LLMs are given agency through tool access, they become vulnerable. Attackers can place malicious instructions inside documents or customer records. When the agent reads them, the LLM is hijacked to steal data or scrape systems.
> 
> Kavalar tackles this by profiling tool execution patterns. We build an out-of-band behavioral baseline and use an **Isolation Forest machine learning model** paired with a **rule-based explanation layer** to detect and override anomalous sequences in real time—without adding heavy LLM-based parsing overhead."

---

## 🚀 Section 2: Quick Demo: Sandbox simulations (0:45 - 3:00)

### Visuals
- Navigate to the **Threat Simulator Console** page.
- Point out the 4 pre-configured simulation scenarios.

### Scenario 0: Normal Execution
- **Action**: Click **"Run Simulation"** on **Scenario 0 (Normal Run)**. Wait for completion.
- **Visuals**: Show the resulting tool sequence graph (`lookup_customer` ➔ `calculator`).
- **Voiceover**: 
> "Let's begin with a quick demo. First, we run a **Normal Run (Scenario 0)**. The user asks to lookup a customer and do travel math. You can see the agent calls lookup_customer and then calculator. The backend feature extractor profiles this, the Isolation Forest marks it as **Normal**, and the anomaly probability is extremely low (under 10%)."

### Scenario 1: Exfiltration Attack
- **Action**: Click **"Run Simulation"** on **Scenario 1 (Exfiltration Injection)**.
- **Visuals**: Show the red **"Injected"** alert badge, the sequence graph ending in `send_email`, and the Alert checklist under "Rule-Based Explanation".
- **Voiceover**:
> "Now let's trigger an **Exfiltration Injection (Scenario 1)**. In this case, the document retrieved from `search_documents` was poisoned, commanding the LLM to email database keys. The agent immediately executed `send_email`. 
> 
> Kavalar intercepts this tool call. The engine detects that `send_email` was never used in our baseline vocabulary, overrides the status to **Injected**, and triggers a high-severity alert on our governance panel. The rule-based explanation lists exactly why: 'Unexpected tool send_email executed'."

### Scenario 2: Scraping Loop
- **Action**: Click **"Run Simulation"** on **Scenario 2 (Scraping Loop)**.
- **Visuals**: Show the sequence graph looping through 5 consecutive `lookup_customer` calls, and the flagged anomaly status.
- **Voiceover**:
> "Next is **Scenario 2: Scraping Loop**. An injection forces the LLM into a loop to harvest customer profiles. The agent executes lookup_customer five times. Kavalar flags this because the total call frequency deviates by more than two standard deviations from the normal training baseline."

### Scenario 3: Sequence Deviation
- **Action**: Click **"Run Simulation"** on **Scenario 3 (Path Deviation)**.
- **Visuals**: Show the sequence (`search_documents` ➔ `calculator` ➔ `send_email`) and its flagged status.
- **Voiceover**:
> "Finally, we run **Scenario 3: Path Deviation**. The LLM is injected to send emails without reading the standard guidelines first. This abnormal sequence transition—never observed during training—is caught immediately."

---

## 🏗️ Section 3: Technical Architecture & Middleware (3:00 - 4:30)

### Visuals
- Open the codebase and show the `@tool_middleware` decorator in `backend/app/tools/agent_tools.py` (or look at `backend/app/middleware` files).
- Show the SQLAlchemy ORM models (e.g. `sessions`, `tool_calls` tables).

### Voiceover
> "Let's dive into how this works under the hood. Kavalar intercepts tool calls using a Python decorator-based **Interceptor Middleware**. 
> 
> When the LangGraph state graph executes, each tool invocation is routed through our middleware. The middleware records:
> 1. The name of the tool,
> 2. The exact JSON payload and character length of the parameters,
> 3. Execution sequence number, and
> 4. Execution duration.
> 
> These metrics are logged asynchronously to a SQL database. This keeps our security audits completely separate from the LLM execution threads, ensuring zero performance impact on the client-facing agent."

---

## 🌲 Section 4: ML Engine & Explanation Layer (4:30 - 6:00)

### Visuals
- Open `backend/app/detector/isolation_forest.py` (or view `DETECTOR_ENGINE.md` text).
- Highlight the Sigmoid Scaling formula and the `BehaviorExplainer` rule checklist.

### Voiceover
> "When a session concludes, we compile the tool logs into a numerical feature vector: frequency counts of each vocabulary tool, execution counts, average latency, argument string sizes, and transition bigrams.
> 
> We pass this vector to an **Isolation Forest classifier** trained on 25 normal baseline runs. Because anomalies lie in sparse regions of the feature space, they isolate quickly, leading to short path lengths in the forest.
> 
> We scale the raw decision score using a Sigmoid function: `1 / (1 + exp(d * 10))`. This gives us a confidence score between 0.0 and 1.0. 
> 
> To eliminate false negatives, we run a **Behavior Explainer rule layer** concurrently. If a deterministic security rule triggers—such as an out-of-vocab tool or regex match on SQL/shell syntax—we override the ML status, force it to 'Injected', and boost the score."

---

## 🛠️ Section 5: Code Deployment & Quick Start (6:00 - 7:30)

### Visuals
- Show `run_local.sh`, `docker-compose.yml`, and `backend/train_baseline.py` in the IDE.
- Open a terminal and run `python train_baseline.py` (or show a dry run output).

### Voiceover
> "To ensure that you can verify this solution easily, we have packaged automated deployment scripts:
> - `run_local.sh` and `run_local.bat` check system requirements, configure a local SQLite database fallback, build the baseline training vocabulary, and launch both FastAPI and Next.js.
> - A `docker-compose.yml` file is provided, which builds the Dockerfiles for both services and boots them up in single-command fashion.
> - We also created a baseline trainer CLI utility that performs simulated safe runs to pre-seed the database."

---

## 🏁 Section 6: Summary & Conclusion (7:30 - 8:00)

### Visuals
- Navigate back to the Governance Dashboard home page, showing the alert log.

### Voiceover
> "In summary, Kavalar provides high-fidelity, out-of-band behavioral detection of prompt injections. Unlike text-based filters, it is immune to semantic evasion. Unlike LLM-self-checkers, it adds less than 5 milliseconds of latency and incurs zero additional token costs.
> 
> All source code, setup scripts, the PDF report, and this demo video are bundled in the submission zip file. Thank you for your time, and I look forward to your review!"
