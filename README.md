# Notion AI Knowledge Bot 🤖

This project integrates Notion, OpenAI's GPT-4, and Slack to create a real-time, context-aware knowledge bot. Users can ask questions in Slack, and the bot will provide answers based on the content stored in a Notion page.

## Getting Started 🚀

### Prerequisites

- Python 3.x
- Notion Account
- Slack Workspace
- OpenAI API key

### Environment Variables 🌍

Create a `.env` file in your root directory and add the following:

\`\`\`env
SLACK_APP_TOKEN=your_slack_app_token
SLACK_BOT_TOKEN=your_slack_bot_token
NOTION_API_KEY=your_notion_api_key
NOTION_PAGE_ID=your_notion_page_id
OPENAI_API_KEY=your_openai_api_key
\`\`\`

### Installation 🛠️

1. Clone the repository:

\`\`\`bash
git clone https://github.com/hollaugo/notion-ai-knowledge-.git
\`\`\`

2. Navigate to the project directory:

\`\`\`bash
cd notion-ai-knowledge-
\`\`\`

3. Install the required packages:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage 🖥️

Run the following command to start the bot:

\`\`\`bash
python app.py
\`\`\`

## Libraries Used 📚

- `openai`
- `requests`
- `python-dotenv`
- `slack_bolt`

## Important Resources 📖

- [OpenAI Documentation](https://platform.openai.com/docs/api-reference/chat)
- [Notion API Documentation](https://developers.notion.com/docs/working-with-page-content)
- [Creating Slack App](https://api.slack.com/apps)
- [Notion Integrations Page](https://www.notion.so/my-integrations)
