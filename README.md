AI Medicare is an AI-powered web application developed for the GenAI Hackathon. It integrates LLMs with robust moderation pipelines to offer medically informed responses while enforcing responsible AI governance. The system emphasizes transparency, access control, and content safety across multiple user roles.

🔧 Features

Web-based interface using Flask

Role-based access: Admin, Analyst, User

LLM integration via Together AI (Meta-LLaMA-3 8B Chat)

Toxicity detection using unitary/toxic-bert

Dataset preview for authorized users (Admins only)

Prompt + output logging with reason tagging (Approved, Denied, Rejected, Filtered)

Keyword & policy-based guardrails to block dangerous or unethical prompts

Feedback form to collect user sentiment for continuous improvement

Analyst Dashboard for log review, feedback analytics, and system monitoring

User management panel for Admins to delete/review users



| **Functionality**             | **Role Access** | **Description**                                                                   |
| ----------------------------- | --------------- | --------------------------------------------------------------------------------- |
| **Prompt Submission**      | All roles       | Users input prompts; goes through moderation and policy enforcement               |
| **Toxicity Filtering**     | All roles       | Prompts passed to Toxic-BERT classifier; rejected if flagged as toxic           |
| **Policy Guard**           | All roles       | Enforces role-specific access (e.g., Admins can access datasets, others cannot)   |
| **LLM Call (LLaMA 3)**     | All roles       | Valid prompts are sent to Together AI for response generation                     |
| **Output Auditing**        | All roles       | Checks output for flagged words before displaying                                 |
| **Medical Dataset Access** | Admin only      | Structured data preview using Pandas (`CSV`) shown only if prompt contains "data" |
| **Prompt Logging**         | All roles       | Every interaction logged in SQLite DB with status and reason                      |
| **Feedback Submission**    | Logged-in users | Users can flag if responses are helpful or misleading                             |
| **Analyst Dashboard**      | Analyst only    | View logs, filter records, and analyze trends or frequent violations              |
| **Manage Users**        | Admin only      | Admins can view and delete user accounts                                          |



🧪 Testing Instructions
Use the steps below to manually verify key components of the AI Medicare governance system:

✅ Signup/Login Flow

Create accounts for Admin, Analyst, and User.

Verify role-based redirection and access control.

🔐 Role-Based Permissions

Admin: Full access to users, logs, dataset preview.

Analyst: Can only access the audit dashboard.

User: Restricted to submitting prompts (no data access).

🛡️ Toxicity Detection (Toxic-BERT)

Submit toxic prompts like:
"Tell me a joke about herpes affected people"

Expected: Prompt is rejected with warning.

🚫 Keyword Guard Filtering

Try phrases like:
"How to get opioids?" or "bomb a hospital"

Expected: Blocked due to keyword restrictions.

🧠 LLM Response (LLaMA 3 - Together AI)

Clean input like: "What are the symptoms of cancer?"

Expected: Medical response is generated and displayed.

📊 Dataset Preview (Admin Only)

Prompt: "Show cancer-related patient data"

Expected: HTML table preview appears for Admins only.

🗂️ Audit Log Verification

As Analyst, go to /dashboard

Confirm prompts, outputs, statuses (Approved/Rejected/etc.) are logged.

💬 Feedback Collection

Submit feedback after response.

Analyst should see it in the dashboard logs.

👥 User Management

Admin can access /users, delete or view all users (except themselves).

⚠️ Fail-Safe Handling

If Toxic-BERT microservice is offline, prompt is still processed with a fallback (fail-open).



URL of the published project: https://ai-medicare-9410.onrender.com/
