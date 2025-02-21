from pymongo import MongoClient
import time
import sys
import os
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# MongoDB URI and collection setup
mongo_uri = "mongodb+srv://cj:1028@cluster0.f9qhs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
collection = client["Cluster0"]["ModmailBots"]

# Values from .env (with error handling)
try:
    search_word = int(os.getenv("USER_ID"))  # Your search _id
    expected_bot_name = os.getenv("BOT_NAME")  # The expected bot name in the DB
    if not expected_bot_name:
        raise ValueError("BOT_NAME is not found.")
except (TypeError, ValueError) as e:
    print(f"Error: {e}")
    sys.exit(1)

# Flag to ensure command is run only once
command_run = False

while True:
    print("Syncing bot presence to the server...")

    # Query all documents in the collection
    documents = collection.find()

    # Loop through all documents in the collection
    for document in documents:
        # Check if the bot is purchased
        purchased = document.get("purchased", False)

        if not purchased:
            print("Bot is not purchased. Ending process...")

            # Get PM2 process list
            result = subprocess.run(["pm2", "list"], capture_output=True, text=True)

            # Check if 'mainmodmail' is in the PM2 list output
            if "mainmodmail" in result.stdout:
                print("Process is still running... terminating.")
                os.system("pm2 delete mainmodmail")

            # Cleanup
            os.system("rm -rf temp/logs")
            sys.exit()

        # Check if bot_name matches
        found_bot_name = document.get("bot_name", "UNKNOWN")
        if found_bot_name != expected_bot_name:
            print(f"Unable to find bot name for _id {document['_id']}, retrying in 5 minutes.")
        else:
            print(f"Bot '{expected_bot_name}' is active, purchased, and name matches for _id {document['_id']}.")

            # Run the command only once if conditions are met
            if not command_run:
                print("Connecting to server...")
                os.system("rm -rf temp/logs")
                os.system("pm2 start bot.sh --name mainmodmail")
                print("Connected to server and started successfully.")
                command_run = True  # Set flag to True to prevent re-running the command
                else:
                print("Synced to server successfully.")
    # Wait for 5 minutes before checking again if bot name doesn't match
    print("No matching bot found, retrying in 5 minutes...")
    time.sleep(300)
