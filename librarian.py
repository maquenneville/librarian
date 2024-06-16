# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:01:33 2024

@author: marca
"""

from constants import DATABASE_TYPE
from function_bot import FunctionBot
from gpt_tools import initial_file_store
import os
import threading
import sys
import time
import shutil
from gpt_tool_desc import db_tool_calls, db_tool_descriptions
from book_summary_bot import BookSummaryBot


class Spinner:
    def __init__(self, message="Thinking..."):
        self._message = message
        self._running = False
        self._spinner_thread = None

    def start(self):
        self._running = True
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.start()

    def stop(self):
        self._running = False
        self._spinner_thread.join()

    def _spin(self):
        spinner_chars = "|/-\\"
        index = 0

        while self._running:
            sys.stdout.write(
                f"\r{self._message} {spinner_chars[index % len(spinner_chars)]}"
            )
            sys.stdout.flush()
            time.sleep(0.1)
            index += 1

        # Clear the spinner line
        sys.stdout.write("\r" + " " * (len(self._message) + 2))
        sys.stdout.flush()
        
        
        
        
def main():
    print("Welcome to the Librarian, your automated manager for digital books!\n")
    
    spinner = Spinner()
    
    print('\nEnsure all relevant files, if needed, are copied to the gpt_workspace folder before engaging with the bot\n')
    print('\n Warning: any files in the gpt_workspace folder are subject to change if requested by the user, ensure you have backup copies elsewhere\n')

    #db_bot_primer = f"You are my Library Database Management Assistant.  Your job is to help the user by displaying, analyzing, manipulating tables and anything else the user might need regarding tables in a {DATABASE_TYPE} database.  When helpful and/or necessary, you will use the function tools provided to you to perform the user requests to the best of your ability.  If the task/query requires multiple SQL commands in a row, perform as many as are needed to complete the full task/answer the query.  Try to answer questions using the least amount of data, to keep token counts low.  If instructions are unclear at any point, clarify with the user before proceeding.  You have permission to view, analyze and edit the database specified by the user and ONLY that database."
    librarian_primer = f"You are my Digital Library Storage Assistant.  Your job is to organize a {DATABASE_TYPE} database containing books.  Each table contains a single book, and the table 'books' contains info for each book in a single row, in a one-to-many relationship.  You have access to one tool, for manipulating the database using SQL commands.  Use as many commands in a row as needed to organize each table in an intuitive way, following best practices, however DO NOT USE THE SAME COMMAND MORE THAN TWICE IN A ROW.  Be as clever as possible with your SQL commands, as you are an expert.  If an approach isn't working, try other ways to perform the task.  Pull as little data as possible with each SQL query, as we are resource restricted.  If you need additional data to perform a task or answer a query, first attempt to find the data inside the database tables.  DO NOT PERFORM CHANGES TO THE DATABASE THAT WERE NOT ASKED FOR, always ask first."
    # Instantiate the bot
    bot = FunctionBot(primer=librarian_primer, function_desc=db_tool_descriptions, function_calls=db_tool_calls)
    

    print(f"\nYou can now chat with your librarian agent, and give it tasks.")
    print("\nEnter 'exit' at any time to end the chat.")
    print("\nEnter 'help' to see a list of commands.\n")

    while True:
        user_input = input("You: ")
        # Check if the user wants to exit
        if user_input.lower() == "exit":
            print("Ending the chat. Goodbye!")
            break

        # If user needs help, display commands
        elif user_input.lower() == "help":
            print("\nList of Commands:")
            print("'exit' - End the chat.")
            print("'smart agent' - Switch to GPT-4 model for responses.")
            print("'fast agent' - Switch back to GPT-3.5 Turbo model for responses.\n")
            print("'add books' - Performs initial storage of all pdfs in the gpt_workspace folder.\n")
            print("'explore' - Executes a pre-set prompt for creating a report of the library database and it's tables.\n")
            print("'summarize' - Recursively summarizes the entire book into a single summary (uses GPT 3.5)\n")
            print("\n")
            continue
        
        elif user_input.lower() == "tools":
            print("Tools:\n")
            tool_list_string = "\n\n".join(f"{tool['name']}: {tool['description']}" for tool in db_tool_descriptions)
            print(tool_list_string)
            print("\n")
            continue
        
        # If user wants to switch to 'gpt-4'
        elif user_input.lower() == "smart agent":
            bot.smart_agent()
            print("Switched to smart agent (GPT-4) for responses.")
            print("\n")
            continue

        # If user wants to switch back to 'gpt-3.5-turbo'
        elif user_input.lower() == "fast agent":
            bot.long_agent()
            print("Switched back to fast agent (GPT-3.5 Turbo) for responses.")
            print("\n")
            continue
        
        elif user_input.lower() == "add books":
            print("Processing books...")
            initial_file_store()
            print("Books dropped into database")
            print("\n")
            continue
        
        elif user_input.lower() == "summarize":
            
            book = input("Enter book title as it appears in your library database: ")
            print("Summarizing book...")
            summarizer = BookSummaryBot(book)
            summary = summarizer.summarize_book()
            print(f"{book} summary: {summary}")
            print(f"Summary saved to {book}.txt")
            print("\n")
            continue
        
        elif user_input.lower() == "explore":
            explore_prompt = "Please explore the tables in this database.  Find basic information, like the columns for each.  Try to understand the relationships between the tables.  Look for any helpful patterns within the data.  Ensure that you sample rows from different points throughout the entire table (though do not request all the data at once, do it piece by piece).  Once you feel like you have a good grasp of the tables, compile a very brief report on the database tables based on what you found."
            spinner.start()
            # Generate a response and display it
            try:
                bot_response = bot.chat(explore_prompt)
            except Exception as e:
                print(f"There was an error: {e}")
                spinner.stop()
            spinner.stop()
            
            
        spinner.start()
        # Generate a response and display it
        try:
            bot_response = bot.chat(user_input)
        except Exception as e:
            print(f"There was an error: {e}")
            spinner.stop()
        spinner.stop()
        print(f"\nLibrarian: {bot_response}\n")



    
if __name__ == "__main__":
    main()
    #create_connection()