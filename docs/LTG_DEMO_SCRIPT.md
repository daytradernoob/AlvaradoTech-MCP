# LTG Demo Script
*Leverage Technology Group | Scottsdale, AZ*
*Target: 10 minutes. One Telegram conversation. Clear before/after.*

---

## Setup (before the call)

- SEi and MSI both running. Verify with watchdog or check Telegram.
- New session started: send `/new` to the bot to clear history.
- Screen share ready: show your phone or Telegram web on your laptop.
- Data files confirmed in `~/.openclaw/workspace/data/ltg/`.

---

## The Frame (say this before touching the phone)

> "I'm going to show you something. This isn't a chatbot. I'm going to ask it a business question — your business — and it's going to answer from your own data. Nothing leaves this machine."

---

## Demo Sequence

### Beat 1 — Identity (30 seconds)

Send: `who are you?`

Expected response:
> "I am MCP — the operating intelligence of this stack. Operator: Rob Alvarado. What do you need?"

**Say:** "That's it. No 'Hi, I'm an AI assistant.' It knows what it is. It knows who it works for."

---

### Beat 2 — The Hook (60 seconds)

Send: `how many accounts have zero security?`

Expected response: Lists the accounts. Flags CRITICAL accounts. Gives a count.

**Say:** "This is your data. 20 sample accounts I built from your service categories. When we load your actual 1,500 — same question, real answer in 30 seconds. Your team currently knows this by memory or by digging through PSA notes. MCP knows it on demand."

---

### Beat 3 — The Number (90 seconds)

Send: `gap analysis`

Expected response: Top 5 ranked opportunities, monthly gap value per account, total pipeline number.

**Say:** "That bottom line — that's money that exists in your current customer base right now. Not prospects. Customers who already trust you, already pay you, and don't have [missing service] yet. Your team can't see this without spending hours in the PSA. MCP sees it in 10 seconds."

---

### Beat 4 — The Drill-Down (60 seconds)

Pick the #1 account from the gap report. Send: `what does [account name] have?`

Expected response: Account lookup — active services, missing services, gap value, notes.

**Say:** "Your account manager walks into a QBR with this. They know exactly what the client has, what they're missing, and what the conversation should be. They're not guessing. They're not winging it."

---

### Beat 5 — The Compliance Angle (60 seconds)

Send: `which accounts are HIPAA exposed?`

Expected response: Medical accounts with no security layer listed with risk flag.

**Say:** "Every medical account you have with no security layer is a liability — for them and for you. This is a conversation you need to have with them anyway. MCP tells you who to call first and why."

---

### Beat 6 — The Close (90 seconds)

Put the phone down.

> "Everything you just saw ran on a Mac Mini M4 Pro. $1,799. Sits in your office. Data never leaves the building. I install it, configure it, hand you the Telegram interface. Your team doesn't need to know anything about AI — they just message it.

> For your 1,500 accounts, that gap report is real money with names on it. The compliance screen is a liability list you can act on. The Q&A is your team having an analyst on call.

> Monthly retainer covers the model, the stack, and me when something needs adjusting. Hardware is a one-time cost.

> What would your team use this for first?"

---

## If They Ask

**"What model is running this?"**
> "Local Ollama model — qwen3:8b right now, tunable up to 70B on better hardware. The Mac Mini I'm recommending runs the 70B. That's frontier quality, locally. Nothing touches OpenAI, nothing touches Anthropic."

**"How does it get our real data?"**
> "CSV export from your PSA — ConnectWise, Autotask, whatever you're using. Drop it in, point MCP at it. Same recipe, real numbers."

**"What about security?"**
> "It runs on your hardware, on your network. No cloud sync. No external API calls unless you ask it to search the web. Your client data never leaves your building."

**"What does it cost?"**
> "Hardware: $1,799 one-time. Install + configuration: flat fee. Monthly retainer: covers support, model updates, and new skill builds as you need them. I'll send you numbers after this call."

**"Can it do [other thing]?"**
> "Probably. Tell me what you need it to do and I'll tell you if it's in scope or on the roadmap."

---

## What You're Measuring

After the demo, answer these:
- Did they ask "what does it cost?" → buying signal
- Did they ask "how do we get our data in?" → buying signal
- Did they say "our team could use this for [X]?" → use case validation
- Did they pull in someone else during the call? → champion signal

---

*This is the LTG demo. Run it clean. The data is the story.*
