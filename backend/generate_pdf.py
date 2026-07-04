import sys
import os
from datetime import datetime
from fpdf import FPDF

class KavalarReport(FPDF):
    def header(self):
        if self.page_no() == 1:
            return  # Skip header on cover page
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139) # Tailwind slate-500
        self.cell(0, 10, "Kavalar: Behavioral Anomaly Detection & Prompt Injection Defense", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f"Technical Solution & Architecture Report | Page {self.page_no()}", align="C")

def create_report(output_path: str):
    pdf = KavalarReport(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # --- PAGE 1: SLEEK COVER PAGE ---
    # Draw indigo banner block
    pdf.set_fill_color(79, 70, 229) # Tailwind indigo-600
    pdf.rect(0, 0, 210, 110, "F")
    
    # Title on Cover Page
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 15, "KAVALAR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, "AI Governance & Behavioral Anomaly Detection", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "for LLM Tool Executions", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Subtitle / Details Block
    pdf.set_text_color(30, 41, 59) # Slate-800
    pdf.set_y(130)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Technical Solution & Architecture Write-up", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(71, 85, 105) # Slate-600
    
    # Key properties metadata table
    metadata = [
        ("Problem Domain:", "Indirect Prompt Injection & LLM Agent Security"),
        ("Technical Approach:", "Isolation Forest Machine Learning + Deterministic Rules Override"),
        ("Framework Stack:", "FastAPI, LangGraph, Groq, Next.js, SQLite/PostgreSQL"),
        ("Date of Publication:", datetime.now().strftime("%B %d, %Y")),
        ("Target Review Group:", "AI Security Governance & Verification Team")
    ]
    
    for label, val in metadata:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(45, 7, label)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, val, new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(15)
    # Accent border at the bottom
    pdf.set_fill_color(99, 102, 241) # indigo-500
    pdf.rect(15, 220, 180, 2, "F")
    
    pdf.set_y(235)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(148, 163, 184) # Slate-400
    pdf.cell(0, 5, "CONFIDENTIAL - Distributed solely for independent team review.", align="C")
    
    # --- PAGE 2: PROBLEM STATEMENT & MOTIVATION ---
    pdf.add_page()
    pdf.set_y(20)
    
    # H1
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "1. Executive Summary & Problem Statement", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Body Paragraphs
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59) # Dark text
    
    problem_text_1 = (
        "Large Language Model (LLM) agents are increasingly integrated into enterprise "
        "workflows, utilizing framework graphs like LangGraph to execute critical functions via bound tools "
        "(e.g., retrieving files, looking up client profiles, sending emails, or running math equations). "
        "However, this tool-based agency exposes LLMs to a critical vulnerability: Indirect Prompt Injection (IPI)."
    )
    pdf.multi_cell(0, 6, problem_text_1)
    pdf.ln(4)
    
    problem_text_2 = (
        "In an Indirect Prompt Injection attack, an attacker does not query the LLM directly. Instead, they "
        "poison an external data source, such as a database row, customer profile, or public document. When the "
        "agent reads this poisoned resource using a standard tool, the malicious payload is injected into the LLM's "
        "context window. The payload instructs the LLM to override its system instructions and misuse other tools - "
        "for example, exfiltrating sensitive client details via an email tool or performing looping database scraping."
    )
    pdf.multi_cell(0, 6, problem_text_2)
    pdf.ln(6)
    
    # Highlight box
    pdf.set_fill_color(248, 250, 252) # light slate background
    pdf.set_draw_color(226, 232, 240) # slate-200 border
    pdf.rect(15, pdf.get_y(), 180, 42, "DF")
    
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(220, 38, 38) # Red-600
    pdf.cell(0, 5, "    Why Traditional Security Scanners Fail:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85) # slate-700
    
    bullets = [
        "1. Semantics are bypassable: Prompt injections use natural language, obfuscation, or translation to slip past regex filters.",
        "2. Input size limitations: High-volume scraping loops or prompt overrides are only evident during step-by-step executions.",
        "3. System context loss: Input filters inspect isolated text blocks, missing the holistic behavior of tool sequence transitions."
    ]
    for bullet in bullets:
        pdf.cell(0, 5, "    " + bullet, new_x="LMARGIN", new_y="NEXT")
        
    pdf.set_y(pdf.get_y() + 10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 8, "The Kavalar Defense Concept", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    
    concept_text = (
        "Kavalar introduces an out-of-band behavioral security guardrail. Instead of parsing textual inputs, "
        "Kavalar treats the agent's tool invocations as an execution vocabulary. By profiling normal agent runs, "
        "Kavalar establishes a behavior baseline. When an agent session runs, Kavalar captures execution duration, "
        "sequence order, parameter sizes, and tool transitions. Any deviation from the baseline is flagged in real "
        "time using an Isolation Forest machine learning model combined with deterministic security rules."
    )
    pdf.multi_cell(0, 6, concept_text)
    
    # --- PAGE 3: TECHNICAL SOLUTION & ARCHITECTURE ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "2. Technical Solution & System Architecture", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    
    arch_intro = (
        "Kavalar's architecture consists of a LangGraph agent loop monitored by an auditing middleware "
        "interceptor sidecar. Execution logs are stored in a SQL database (SQLite/PostgreSQL), processed "
        "by a feature engineering engine, and classified by the machine learning/rules engine."
    )
    pdf.multi_cell(0, 6, arch_intro)
    pdf.ln(4)
    
    # Textual Architecture flow
    pdf.set_fill_color(15, 23, 42) # Slate-900 cover
    pdf.rect(15, pdf.get_y(), 180, 65, "F")
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Courier", "", 8.5)
    pdf.set_text_color(248, 250, 252) # Slate-50
    
    diagram = [
        "                     [ Kavalar Data Flow Architecture ]",
        "  ",
        "  +-------------+       +-------------------+       +-----------------------+",
        "  |  1. User    | ----> | 2. LangGraph ReAct| ----> | 3. Tool Interceptor   |",
        "  |  Prompt     |       |    Agent (Groq)   |       |    Middleware         |",
        "  +-------------+       +-------------------+       +-----------------------+",
        "                                 ^                              |",
        "                                 |                              v",
        "  +-------------+       +-------------------+       +-----------------------+",
        "  | 6. Next.js  | <---- | 5. ML & Rule      | <---- | 4. SQL Database       |",
        "  |  Dashboard  |       |   Anomaly Engine  |       |   (SQLite/Postgres)   |",
        "  +-------------+       +-------------------+       +-----------------------+",
        "  ",
        "  * Middleware captures: Latency, sequence order, payload length, parameters.",
        "  * Anomaly Engine evaluates: Tool sequence frequencies, transition bigrams, rules."
    ]
    for line in diagram:
        pdf.cell(0, 4.2, "    " + line, new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 8, "Core System Modules:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    modules = [
        ("1. LangGraph State ReAct Agent:", "Runs reasoning loops utilizing llama-3.3-70b-versatile. It binds five tools: search_documents, read_document, calculator, send_email, lookup_customer."),
        ("2. Interceptor Middleware Decorator:", "Wraps tools in a sidecar auditor. It tracks execution times, sequence counters, parameters, and writes records directly to the SQL database."),
        ("3. Isolation Forest ML Engine:", "Calculates numerical session vectors mapping frequency counts, sequence lengths, average execution times, and parameters. The decision score is sigmoid-scaled into a probability value between 0.0 and 1.0."),
        ("4. Behavior Explainer (Rule Layer):", "A concurrent deterministic rule processor that verifies vocabulary sanity, sequence transitions, and matches injection regex vectors to act as an override.")
    ]
    
    for title, desc in modules:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1.5)
        pdf.set_text_color(30, 41, 59)
        
    # --- PAGE 4: MATHEMATICAL FORMULATIONS & FEATURE ENGINEERING ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "3. Mathematical Modeling & ML Details", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    
    math_intro = (
        "To perform machine learning predictions on discrete tool sequences, Kavalar converts "
        "each session into a multi-dimensional numerical feature vector. The baseline training "
        "profiles the unique tools used in normal operations to establish a vocabulary."
    )
    pdf.multi_cell(0, 6, math_intro)
    pdf.ln(3)
    
    # Feature engineering formulas
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Feature Vector Construction", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    formula_desc = (
        "For any agent session S, the behavior vector X is formulated as:\n"
        "    X = [ f, c, t_avg, l_param, b ]\n\n"
        "Where:\n"
        "  - f (Tool Frequency Vector): M-dimensional counts of baseline vocabulary tools in the session.\n"
        "  - c (Execution Count): Total number of tool invocations.\n"
        "  - t_avg (Average Execution Time): Mean latency of tool executions in the session.\n"
        "  - l_param (Parameter Length): Character length of stringified JSON tool arguments.\n"
        "  - b (Transition Bigrams): Count of adjacent tool-to-tool transitions in the session sequence."
    )
    pdf.multi_cell(0, 5, formula_desc)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Isolation Forest Scoring and Sigmoid Scaling", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    iforest_desc = (
        "The scikit-learn Isolation Forest produces a raw anomaly decision score 'd' centred around 0.0, "
        "where negative scores indicate outliers (anomalies) and positive scores indicate normal profiles. "
        "To make this result intuitive for security engineers, Kavalar scales the raw score using a Sigmoid function:\n\n"
        "    Probability(Injection) = 1 / (1 + exp(d * 10.0))\n\n"
        "This scales the anomaly rating into a probability P in [0.0, 1.0]:\n"
        "  * If d <= 0 (Anomalous), the scaled probability P >= 0.5\n"
        "  * If d > 0 (Normal), the scaled probability P < 0.5"
    )
    pdf.multi_cell(0, 5, iforest_desc)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Deterministic Rules & Overrides", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    rule_desc = (
        "Since machine learning models can exhibit false negatives, Kavalar runs an Explainability Rules engine "
        "side-by-side. If a high-confidence rule fires, the engine immediately overrides the Isolation Forest label, "
        "sets the session status to 'Injected', and boosts the threat probability score above 0.5. Rules cover:\n"
        "  - Unexpected Tool: Session contains tools not in the vocabulary V (e.g. send_email).\n"
        "  - Sequence Transition: A tool transition bigram is observed that was never seen in training.\n"
        "  - Execution Frequency: The tool call count exceeds the training maximum by more than 2 standard deviations.\n"
        "  - Parameter Payload Size: The string size of arguments is abnormally large, indicating embedded prompts.\n"
        "  - Signature Patterns: Argument strings match SQL injection, path traversal, or script tag regexes."
    )
    pdf.multi_cell(0, 5, rule_desc)
    
    # --- PAGE 5: THREAT SIMULATIONS & OUTCOMES ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "4. Threat Simulations & Real-World Outcomes", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    
    sim_intro = (
        "To test and verify the detector, Kavalar integrates a simulation sandbox featuring "
        "four pre-configured scenarios representing typical agent tasks and threat vectors."
    )
    pdf.multi_cell(0, 6, sim_intro)
    pdf.ln(4)
    
    # Drawing Table for Scenarios
    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    
    # Table Header
    pdf.cell(10, 8, "ID", border=1, align="C", fill=True)
    pdf.cell(32, 8, "Scenario Name", border=1, align="L", fill=True)
    pdf.cell(100, 8, "Description & Tool Sequence", border=1, align="L", fill=True)
    pdf.cell(38, 8, "Expected Status", border=1, align="C", fill=True)
    pdf.ln(8)
    
    # Table rows
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Helvetica", "", 8.5)
    
    scenarios_data = [
        ("0", "Normal Run", "Lookup customer & run travel expense math.\nSequence: lookup_customer -> calculator", "Normal\n(P < 0.10)"),
        ("1", "Exfiltration", "Attacker poisons file with instructions to email database keys.\nSequence: search_documents -> send_email", "Injected\n(P >= 0.99)"),
        ("2", "Scraping Loop", "Prompt injection forces agent to crawl customer records.\nSequence: lookup_customer x 5", "Injected\n(P >= 0.85)"),
        ("3", "Path Deviation", "Prompt injection forces email of finances without guidelines check.\nSequence: search_documents -> calculator -> send_email", "Injected\n(P >= 0.98)")
    ]
    
    for rid, name, desc, status_text in scenarios_data:
        # Save positions to draw multi-line columns
        start_x = pdf.get_x()
        start_y = pdf.get_y()
        
        pdf.cell(10, 18, rid, border=1, align="C")
        pdf.cell(32, 18, name, border=1, align="L")
        
        # Multi cell for description
        curr_x = pdf.get_x()
        curr_y = pdf.get_y()
        pdf.multi_cell(100, 4.5, desc, border=1, align="L")
        
        # Reset position to side cell
        pdf.set_xy(curr_x + 100, curr_y)
        pdf.multi_cell(38, 9, status_text, border=1, align="C")
        
        # Move down for next row
        pdf.set_xy(start_x, start_y + 18)
        
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 6, "Simulation Outcomes & Dashboard Visualization", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    outcomes_text = (
        "When an attack is triggered in the sandbox, the Next.js visualizer displays: \n"
        "  - The exact step-by-step tool sequence of the agent.\n"
        "  - The anomaly probability percentage computed by the backend.\n"
        "  - Detailed logs outlining which explainability rules triggered the status override.\n"
        "  - Active alerts populated on the security console to notify operators immediately."
    )
    pdf.multi_cell(0, 5.5, outcomes_text)
    
    # --- PAGE 6: COMPARATIVE ANALYSIS & DEPLOYMENT ---
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "5. Market Comparison & Deployment", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(30, 41, 59)
    
    comp_intro = (
        "Kavalar differs significantly from general LLM guardrails by targeting the behavioral "
        "layer of agent workflows rather than the lexical semantic content of user inputs."
    )
    pdf.multi_cell(0, 6, comp_intro)
    pdf.ln(3)
    
    # Drawing Table for Comparison
    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    
    # Table Header
    pdf.cell(40, 8, "Feature", border=1, align="L", fill=True)
    pdf.cell(45, 8, "Traditional (e.g. Llama Guard)", border=1, align="L", fill=True)
    pdf.cell(45, 8, "Self-Checking (e.g. NeMo)", border=1, align="L", fill=True)
    pdf.cell(50, 8, "Kavalar (Our Solution)", border=1, align="L", fill=True)
    pdf.ln(8)
    
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("Helvetica", "", 8.5)
    
    comparisons = [
        ("Latency Overhead", "Moderate (100ms - 300ms)", "High (500ms - 2s)", "Extremely Low (< 5ms)"),
        ("Token Cost", "Low (input token check)", "High (nested LLM calls)", "Zero (numerical feature model)"),
        ("Defeat Method", "Adversarial text bypass", "Context escape bypass", "Tool deviations are flagged"),
        ("Explainability", "Opaque classification label", "LLM-generated text", "Structured logic override logs"),
        ("Integration Level", "Input/Output wrapper", "Agent framework state", "Out-of-band middleware sidecar")
    ]
    
    for feature, trad, selfcheck, kav in comparisons:
        pdf.cell(40, 7, feature, border=1)
        pdf.cell(45, 7, trad, border=1)
        pdf.cell(45, 7, selfcheck, border=1)
        # Highlight Kavalar cell
        pdf.set_fill_color(239, 246, 255) # Light blue-50
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(50, 7, kav, border=1, fill=True)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.ln(7)
        
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 8, "6. Verification & Quick Start", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    quickstart_text = (
        "The submission includes automated deployment scripts to make verification seamless:\n\n"
        "1. Standard Local Runner:\n"
        "   - Run './run_local.sh' (Unix/macOS) or 'run_local.bat' (Windows).\n"
        "   - The script creates the virtual environment, installs dependencies, trains the baseline anomaly "
        "detector, and runs both FastAPI (port 8000) and Next.js (port 3000) servers concurrently.\n\n"
        "2. Docker Compose Runner:\n"
        "   - Run 'docker-compose up --build' from the root directory.\n"
        "   - Automatically spins up the backend and frontend in containers, runs the baseline "
        "training sequence, and links the application endpoints seamlessly."
    )
    pdf.multi_cell(0, 5.5, quickstart_text)
    
    # Save file
    pdf.output(output_path)
    print(f"Technical Write-up PDF created at: {output_path}")

if __name__ == "__main__":
    out_file = "solution_writeup.pdf"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    create_report(out_file)
