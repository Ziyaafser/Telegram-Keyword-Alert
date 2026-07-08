# Telegram Keyword Alert

This watches Telegram messages that your own account can already see and sends a Windows notification when one of these phrases appears:

- `larkin sentral`
- `larkin`
- `jb sentral`

## Why this is not a normal bot

Telegram bots in groups run in Privacy Mode by default, so they only see commands, direct mentions, and a few service messages unless the bot is added to the group and privacy is disabled. If you are just a member of the group and cannot add or configure a bot, use this client-based watcher instead.

## Setup

1. Install Python 3.10 or newer.
2. Go to <https://my.telegram.org/apps> and create an app.
3. Copy the `api_id` and `api_hash`.
4. In this folder, create your `.env` file:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

5. Put your real values in `.env`.
6. Install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

7. Run the watcher:

   ```powershell
   .\.venv\Scripts\python.exe -u telegram_alert.py
   ```

The first run asks for your Telegram phone number, login code, and possibly your two-factor password. A local `telegram_alert_session.session` file is created so you do not need to log in every time.

If the interactive login prompt does not accept input, run:

```powershell
python login.py
python login.py YOUR_CODE_HERE
```

Then run `.\.venv\Scripts\python.exe -u telegram_alert.py` again.

## Watch only one group

By default the script watches all chats your account can see. To limit it:

```powershell
python list_chats.py
```

Copy the group title, username, or numeric ID into `.env`:

```text
TARGET_CHATS=Example Work Group
```

For multiple chats:

```text
TARGET_CHATS=Example Work Group,-1001234567890
```

## Add or change keywords

Edit `KEYWORDS` in `.env`:

```text
KEYWORDS=larkin sentral,larkin,jb sentral
```

Add more phrases by separating them with commas:

```text
KEYWORDS=larkin sentral,larkin,jb sentral,senai airport,customs
```

Matching is not case-sensitive, so `larkin`, `Larkin`, and `LARKIN` all trigger the same alert.

After changing `KEYWORDS`, stop and restart `telegram_alert.py`.

## Keep it running

To run the watcher manually, open PowerShell and run:

```powershell
cd C:\Users\User\Desktop\Telegram_Alert
.\.venv\Scripts\python.exe -u telegram_alert.py
```

Leave that PowerShell window open while you want alerts running.

## Start automatically with Windows Task Scheduler

Use Task Scheduler if you want the watcher to start automatically when you log in to Windows.

1. Open **Task Scheduler**.
2. Click **Create Task**.
3. In **General**:
   - Name: `Telegram Alert Watcher`
   - Select: `Run only when user is logged on`
   - Tick: `Run with highest privileges`
4. In **Triggers**:
   - Click **New**
   - Begin the task: `At log on`
   - Click **OK**
5. In **Actions**:
   - Click **New**
   - Action: `Start a program`
   - Program/script:

     ```text
     C:\Users\User\Desktop\Telegram_Alert\.venv\Scripts\python.exe
     ```

   - Add arguments:

     ```text
     -u telegram_alert.py
     ```

   - Start in:

     ```text
     C:\Users\User\Desktop\Telegram_Alert
     ```

   - Click **OK**
6. In **Conditions**:
   - Untick: `Start the task only if the computer is on AC power`
7. In **Settings**:
   - Tick: `Allow task to be run on demand`
   - Tick: `Restart on failure`
   - Restart every: `1 minute`
   - Attempt restart up to: `3 times`
8. Click **OK**.

To test it, right-click `Telegram Alert Watcher` in **Task Scheduler Library** and click **Run**. If it starts correctly, the task status should show `Running`.
