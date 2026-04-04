# Customer Install Playbook
*AlvaradoTech-MCP | Target: under 30 minutes*

---

## Before You Arrive

**Hardware confirmed:**
- [ ] Mac Mini M4 Pro 48GB (Track A) — or designated on-prem machine
- [ ] Machine has internet access at customer site

**Accounts confirmed:**
- [ ] Telegram bot created via @BotFather (takes 2 minutes, do this ahead)
- [ ] Customer's Telegram user ID (they message @userinfobot)
- [ ] Anthropic API key if doing Track B

**Data ready (if doing account intelligence skills):**
- [ ] Customer's account list exported from PSA (CSV format)
- [ ] Their service catalog with pricing (can build this together on-site)

---

## Track A — On-Prem (Mac Mini or dedicated machine)

*Full data sovereignty. No API keys required. Local inference only.*

### Step 1 — Install Ollama (5 min)

```bash
# macOS
brew install ollama
brew services start ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

Verify: `ollama list` — should return without error.

### Step 2 — Install Node.js 20+ (2 min, skip if already installed)

```bash
# macOS
brew install node

# Linux (Ubuntu)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 3 — Clone repo and run setup (15 min — model download is the wait)

```bash
git clone https://github.com/daytradernoob/AlvaradoTech-MCP.git
cd AlvaradoTech-MCP
bash deploy/onprem-setup.sh
```

The script will:
- Install OpenClaw
- Pull qwen3:8b and create mcp-qwen3 (8k context) — **this is the slow step, ~10 min on first run**
- Prompt for Telegram bot token and user ID
- Generate openclaw.json automatically
- Copy workspace files
- Start the gateway

### Step 4 — Verify (2 min)

Message the Telegram bot: `who are you?`

Expected: `I am MCP — the operating intelligence of this stack.`

If that lands, the platform is running.

### Step 5 — Load customer data (5 min)

```bash
mkdir -p ~/.openclaw/workspace/data/customer
# Copy customer's account CSV:
cp /path/to/their-accounts.csv ~/.openclaw/workspace/data/customer/accounts.csv
# Copy their service catalog:
cp /path/to/their-catalog.csv ~/.openclaw/workspace/data/customer/service_catalog.csv
```

Test in Telegram: `gap analysis`

---

## Track B — VPS Cloud

*No hardware required. Claude API for inference. ~$50-70/month running cost.*

```bash
# On a fresh Ubuntu 22.04 VPS (Hetzner CX32 recommended)
git clone https://github.com/daytradernoob/AlvaradoTech-MCP.git
cd AlvaradoTech-MCP
bash deploy/vps-setup.sh
```

Requires: Telegram bot token, Anthropic API key. See `deploy/.env.example`.

---

## Post-Install Checklist

**Platform:**
- [ ] `who are you?` → responds as MCP
- [ ] `gap analysis` → returns account report (uses sample data if no customer data loaded)
- [ ] Watchdog running on Pi-4 or equivalent (optional but recommended)

**Customer data:**
- [ ] `data/customer/accounts.csv` loaded
- [ ] `data/customer/service_catalog.csv` loaded
- [ ] `gap analysis` returns their real accounts
- [ ] `how many accounts have no security?` returns accurate count

**Handoff:**
- [ ] Customer knows their Telegram user ID is the only authorized interface
- [ ] Customer has been walked through 3-5 example queries
- [ ] Rob's retainer contact info is saved in the bot's first response or welcome message

---

## Customizing the Agent for the Customer

Edit these files in `~/.openclaw/workspace/` to make the agent theirs:

| File | What to change |
|---|---|
| `SOUL.md` | Add customer's company name and context to the Stack section |
| `IDENTITY.md` | Optional: rename the agent (default: MCP) |
| `USER.md` | Run the onboarding interview — or fill manually if you know their profile |

Keep edits minimal. The platform works out of the box. Only customize what adds value.

---

## If Something Breaks

**Bot not responding:**
```bash
openclaw gateway status
openclaw gateway restart
```

**Model producing garbage output:**
```bash
# Confirm mcp-qwen3 is the active model
grep primary ~/.openclaw/openclaw.json
# Should show: "ollama/mcp-qwen3"

# Check Ollama is running
curl http://localhost:11434/api/tags
```

**Session acting strange:**
```bash
# Clear session history (keeps config and workspace)
echo '{}' > ~/.openclaw/agents/main/sessions.json
rm ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null
openclaw gateway restart
```

**Check the logs:**
```bash
openclaw gateway logs --tail 50
```

---

## Hardware Reference

| SKU | Use case | Cost |
|---|---|---|
| Mac Mini M4 Pro 48GB | Track A — recommended. Runs 70B models. | ~$1,799 |
| Any machine with 16GB+ RAM | Track A — minimum viable | Hardware you own |
| Hetzner CX32 VPS | Track B — cloud | ~$20/month |

---

## Time Estimates

| Task | Time |
|---|---|
| Telegram bot setup (BotFather) | 2 min |
| Ollama + Node.js install | 5 min |
| Model download (first time) | 10-15 min |
| `onprem-setup.sh` (after model) | 5 min |
| Customer data load + verify | 5 min |
| **Total** | **~25-30 min** |

Model download is the only variable. On subsequent installs the model may already be on the machine or pullable from cache.

---

*This is the install playbook. Every customer deployment follows this sequence.*
*Customer-specific notes go in `~/.openclaw/workspace/docs/customers/[name]/INSTALL_NOTES.md`*
