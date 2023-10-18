import requests
from dotenv import load_dotenv
import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler




# Load environment variables from .env file
load_dotenv()
notion_page_id = os.getenv("NOTION_PAGE_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")




def fetch_notion_page_blocks(page_id, page_size=100):
    """
    Fetch all blocks (children) of a Notion page by its ID, handling pagination.
    
    Parameters:
        page_id (str): The ID of the Notion page to fetch blocks for.
        page_size (int): The number of blocks to fetch per request (max 100).
        
    Returns:
        list: A list of JSON objects representing each block.
    """
    api_key = os.getenv("NOTION_API_KEY")
    url = f'https://api.notion.com/v1/blocks/{page_id}/children'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Notion-Version': '2022-06-28'
    }
    
    all_blocks = []
    start_cursor = None
    
    while True:
        params = {'page_size': page_size}
        if start_cursor:
            params['start_cursor'] = start_cursor
            
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            json_response = response.json()
            
            all_blocks.extend(json_response.get('results', []))
            
            if not json_response.get('has_more', False):
                break
                
            start_cursor = json_response.get('next_cursor')
            
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
    
    return all_blocks


def extract_documents_from_blocks(blocks):
    """
    Extract and format all the content text into an array of strings.
    
    Parameters:
        blocks (list): A list of JSON objects representing each block.
        
    Returns:
        list: An array of strings containing the text content from the blocks.
    """
    documents = []
    for block in blocks:
        block_type = block.get('type')
        
        # Check for types of blocks that contain text
        if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'numbered_list_item', 'bulleted_list_item']:
            rich_text = block.get(block_type, {}).get('rich_text', [])
            
            # Concatenate all the text elements in the rich_text field
            text_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            
            if text_content:  # Only add non-empty strings
                documents.append(text_content)
        
        # Check for code blocks
        elif block_type == 'code':
            code_block = block.get('code', {})
            rich_text = code_block.get('rich_text', [])
            
            # Concatenate all the text elements in the rich_text field
            code_content = ''.join([text.get('text', {}).get('content', '') for text in rich_text])
            
            if code_content:  # Only add non-empty strings
                documents.append(code_content)
                
    return documents

def query_openai_with_documents(documents, user_query):
    """
    Query OpenAI GPT-4 based on the provided documents and user query.
    
    Parameters:
        documents (list): A list of strings containing the text content from the blocks.
        user_query (str): The user's query to be answered by the model.
        
    Returns:
        dict: A dictionary containing the model's answer.
    """
    # Convert the list of documents into a single string
    context = "\n".join(documents)
    
    # Create the system message with the context
    system_message = {
        "role": "system",
        "content": f"You are a helpful assistant who will answer questions based on a document containing information about a course. It includes video narrations and explanations of concepts and code snippets. Use Slack markdown to return information especially around headings, code blocks, bullet points as well as using bold and italics where necessary, add emojis where necessary. You will use the context provided below from this document to answer accurate questions. In scenarios where code is not clean for code snippet, format accordingly\n\nContext \n{context}\n\nResponse\n"
    }
    
    # Create the user message
    user_message = {
        "role": "user",
        "content": user_query
    }
    
    # Make the API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[system_message, user_message],
        temperature=0,
        max_tokens=3256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # Extract and format the assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    formatted_reply = {"answer": assistant_reply}
    
    return formatted_reply



app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("")
def message_hello(client, message, say):
    # Your existing logic here
    channel_id = message['channel']
    user_id = message['user']
    
    # Send an initial message saying "Working on it..."
    ts = say(text="Working on it...", channel=channel_id, thread_ts=message['ts'])['ts']
    
    # Fetch documents and query OpenAI
    blocks = fetch_notion_page_blocks(notion_page_id)
    documents = extract_documents_from_blocks(blocks)
    user_query = message['text']
    answer = query_openai_with_documents(documents, user_query)
    
    # Extract the text value from the answer dictionary
    answer_text = answer.get('answer', 'No answer available.')
    
    # Update the initial message with the answer, in the same thread
    client.chat_update(
        channel=channel_id,
        ts=ts,
        text=answer_text,
        thread_ts=message['ts']  # This ensures the message is in the same thread
    )

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()