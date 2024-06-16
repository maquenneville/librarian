# Librarian

**Librarian** is your automated manager for digital books. This program helps you manage and interact with a digital library database, handling tasks such as adding books, exploring the database, and summarizing book content.

## Features

- **Dynamic SQL Execution**: The bot can perform any task within the library database using SQL commands.
- **Maintain Books Table**: Automatically update the "books" table with more records.
- **Chapter Identification**: Find and label chapters within books.
- **Word Count Calculation**: Calculate and update word counts for each section of a book.
- **Comprehensive Summarization**: Create a summary of an entire book using recursive summarization techniques.
- **Database Exploration**: Generate detailed reports of the library database, including table structures and relationships.
- **Adaptive Response**: Switch between fast responses using GPT-3.5 Turbo and more sophisticated responses using GPT-4.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/librarian.git
    cd librarian
    ```

2. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

3. Update the `config.ini` file in the root directory with your API key and personal database info


## Usage

1. **Navigate to the Project Directory**:
    ```bash
    cd path/to/librarian
    ```

2. **Ensure Files are in the `gpt_workspace` Folder**:
    Copy all relevant book pdf files into the `gpt_workspace` folder before starting the bot.

3. **Start the Librarian**:
    ```bash
    python librarian.py
    ```

4. **Interact with the Bot**:
    - Once the program is running, you can communicate with the bot via natural language or give it commands.
    - Type `help` to get a list of available commands.


## Example Interaction

```plaintext
Welcome to the Librarian!

Ensure all relevant files are copied to the gpt_workspace folder before engaging with the bot.
Warning: any files in the gpt_workspace folder are subject to change, ensure you have backup copies elsewhere.

You can now chat with your librarian agent and give it tasks.
Enter 'exit' to end the chat.
Enter 'help' to see a list of commands.

You: add books
Processing books...
Books dropped into database

You: summarize
Enter book title as it appears in your library database: Example Book
Summarizing book...
Example Book summary: [Generated summary]
Summary saved to Example Book.txt
```

## Notes

- Ensure all necessary files are in the `gpt_workspace` folder before starting.
- Make backup copies of important files before using `add books`.
- Summarizing a book may take some time due to recursive summarization techniques.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


