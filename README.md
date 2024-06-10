
# Discord Bot 🤖

A Discord bot that interacts with users for verification and other commands.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Commands](#commands)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- Verify users via Twitter handle and verification code 🐦
- Manage roles based on verification status 🛡️
- Clear messages from the channel 🧹
- Interact with Google Sheets for data storage 📊
- Post memes from a GitHub repository every 6 hours 🎉
- Ensure no meme is posted more than once 🚫

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/gaulerie/latl-discord.git
   cd latl-discord
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Discord token (in GitHub, create a Secret):

   ```env
   DISCORD_TOKEN=your_discord_token_here
   ```

## Usage

Run the bot:

```bash
python bot.py
```

## Commands

- `!verify [@ Twitter]` - Starts the verification process. ✅
- `!check [tweet link]` - Verifies the tweet with the verification code. 🔍
- `!clear [number of messages]` - Deletes the specified number of messages in the channel. 🧼
- `!bothelp` - Lists available commands. 📜

## Deployment

This bot can be deployed using GitHub Actions.

### GitHub Actions Setup

1. Create a file named `post_meme.yml` in the `.github/workflows` directory:

   ```yaml
   name: Post Meme to Discord

   on:
     schedule:
       - cron: '0 */6 * * *'
     workflow_dispatch:

   jobs:
     post-meme:
       runs-on: ubuntu-latest

       steps:
       - name: Checkout repository
         uses: actions/checkout@v2

       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: 3.8

       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install discord.py requests

       - name: Run post meme script
         env:
           DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
         run: |
           python auto_meme_post.py
   ```

2. Add your `DISCORD_TOKEN` to the repository secrets:

   - Go to `Settings > Secrets and variables > Actions`.
   - Click `New repository secret`.
   - Add a new secret with the name `DISCORD_TOKEN` and your Discord bot token as the value.

## Contributing

1. Fork the repository. 🍴
2. Create your feature branch (`git checkout -b feature/AmazingFeature`). 🌟
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`). 📝
4. Push to the branch (`git push origin feature/AmazingFeature`). 🚀
5. Open a pull request. 📬

## License

Distributed under the MIT License. See `LICENSE` for more information.
