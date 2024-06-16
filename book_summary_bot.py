# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 22:35:58 2024

@author: marca
"""
from simple_bot import SimpleBot
from constants import DATABASE_TYPE, DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
from gpt_tools import get_engine_string
from sqlalchemy import create_engine, text
import time




book_summary = "You are my Book Summary Assistant.  Your job is to take either a group of pages or group of summaries.  You will then summarize the text, preserving as many details as possible.  You must respond with a summary, and only a summary, no explanatory text or pleasantries."

class BookSummaryBot(SimpleBot):
    
    def __init__(self, table_name, model="gpt-3.5-turbo"):
        super().__init__( primer=book_summary, model=model)
        #print("Initializing book pages and summary groups...")
        self.table_name = table_name
        self.page_texts = self._fetch_all_page_texts(self.table_name)
        self.groups = self.group_book_pages(self.page_texts)
        self.group_summaries = []
        #print("Initialization complete")
        
        
    def _fetch_all_page_texts(self, table_name):
        """
        Fetches all values of the page_text column from the specified table in the database.
        
        Args:
            table_name (str): The name of the table in the database.
            
        Returns:
            list: An array of text values from the page_text column.
        """
        conn_str = get_engine_string()
        engine = create_engine(conn_str)
        connection = None
        page_texts = []
    
        try:
            connection = engine.connect()
            result = connection.execute(text(f"SELECT page_text FROM {table_name}"))
            page_texts = [row[0] for row in result]  # Accessing the first element of each row tuple
        except Exception as e:
            print(f"An error occurred while fetching page texts: {e}")
        finally:
            if connection:
                connection.close()
            if engine:
                engine.dispose()
    
        return page_texts

    def group_book_pages(self, page_texts, max_token_length=10000):
        """
        Groups an array of page text values into text blocks based on a maximum token length.
        
        Args:
            page_texts (list): An array of page text values.
            max_token_length (int): The maximum token length for a text block.
            
        Returns:
            list: An array of text blocks, each within the specified token limit.
        """
        grouped_pages = []
        current_group = ""

        for page_text in page_texts:
            # Check if adding the current page to the current group would exceed the token limit
            if self.count_tokens(current_group + page_text) > max_token_length:
                # If so, and the current group isn't empty, add it to the groups and start a new one
                if current_group:
                    grouped_pages.append(current_group.strip())
                    current_group = page_text
                else:
                    # If the current group is empty (a single page exceeds the limit), add the page directly
                    grouped_pages.append(page_text)
            else:
                # If not, add the current page to the current group
                current_group += " " + page_text

        # Add the last group if it's not empty
        if current_group:
            grouped_pages.append(current_group.strip())

        return grouped_pages
    

    def _summarize_text(self, input_string: str):
        # Create a local copy of self.primer
        messages = self.primer.copy()
        
        # Append new user message
        messages.append({"role": "user", "content": f"Text to summarize: {input_string}"})
        
        response = self._generate_response(messages, temperature=0.1)
        print(response)
        
        return response.choices[0].message.content

    def summarize_page_groups(self):
        """
        Summarizes each group of page texts in self.summary_groups.
        
        Returns:
            list: An array of summaries, one for each group in self.summary_groups.
        """
        summaries = []
        for group in self.groups:
            print("Summarizing group...")
            summary = self._summarize_text(group)
            summaries.append(summary)
            print("Summary complete")
            
        self.group_summaries = summaries
        return summaries
    
    def recursive_summary(self, texts, max_token_length=10000):
        """
        Recursively groups and summarizes texts until a single summary is produced.
        
        Args:
            texts (list): An array of text values to be summarized.
            max_token_length (int): The maximum token length for a text block.
            
        Returns:
            str: The final summary of all texts.
        """
        # Base case: if there's only one text, return it
        if len(texts) == 1:
            return texts[0]
    
        # Group the texts
        grouped_texts = self.group_book_pages(texts, max_token_length)
    
        # Summarize each group
        summaries = []
        for group in grouped_texts:
            summary = self._summarize_text(group)
            summaries.append(summary)
    
        # Recursively summarize the summaries
        return self.recursive_summary(summaries, max_token_length)
    
    def summarize_book(self):
        """
        Summarizes the entire book recursively until a single main summary is produced.
        
        Returns:
            str: The final summary of the book.
        """
        start_time = time.perf_counter()
        
        final_summary = self.recursive_summary(self.page_texts)
        
        # Save the final summary to a .txt file
        file_name = f"{self.table_name}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(final_summary)
        
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        print(f"Final summary saved to {file_name}")
        print(f"Processing time: {processing_time:.2f} seconds")
        
        return final_summary