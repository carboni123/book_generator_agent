# main.py
from agents.writer.writer_agent import WriterAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from api.openai_api import OpenAIAPI
from api.google_api import GoogleAPI
from exporter import PDFExporter
from filter import Filter
import random
import time
import argparse
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_input():
    """
    Gets the user input or generates random input if the user chooses.

    Returns:
        str: The user input or a random input.
    """
    use_random = input("Generate random input? (yes/no): ").lower() == "yes"
    if use_random:
        input_options = ["A fantasy adventure in a magical kingdom", "A sci-fi thriller on a space station",
                        "A mystery in a haunted house", "A romance between a detective and a suspect"]
        return random.choice(input_options)
    else:
        return input("Enter the book's theme: ")

def create_api_instance(api_type, api_key):
    if api_type == "openai":
        return OpenAIAPI(api_key=api_key)
    elif api_type == "google":
        return GoogleAPI(api_key=api_key)
    else:
        raise ValueError(f"Invalid API type: {api_type}")

async def generate_and_review(writer, reviewer, input_prompt, log_filename, exporter, filter, epoch):
    """
    Generates and reviews a book, with a timeout for api calls
    """
    try:
            # Generate Book
            book = await writer.generate_book(input_prompt)
            
            # Save book content to a txt file
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            book_filename = f"book_{timestamp}_epoch{epoch + 1}.txt"
            
            with open(os.path.join(exporter.output_dir, book_filename), "w", encoding="utf-8") as file:
              file.write(book)
            logging.info(f"Book content saved to: {exporter.output_dir}/{book_filename}")


            # Review Book
            score, feedback = await reviewer.review_book(book, input_prompt)
            logging.info(f"Review Score: {score}")
            logging.info(f"Review Feedback: {feedback}\n")
            
            with open(log_filename, "a", encoding="utf-8") as log_file:
                log_file.write(f"Epoch: {epoch + 1}, Score: {score}, Feedback: {feedback}\n")
            return book, score, feedback
    
    except Exception as e:
            logging.error(f"An error occurred during iteration {epoch + 1}: {e}")
            return None, 0, f"An error occurred during iteration {epoch + 1}: {e}"

async def main():
    """
    Main function to run the AI book generator.
    """
    parser = argparse.ArgumentParser(description="AI Book Generator")
    parser.add_argument("--api", type=str, default="openai", choices=["openai", "google"], help="API to use (openai, google)")
    parser.add_argument("--api_key", type=str, help="API key for the selected API")
    parser.add_argument("--max_iterations", type=int, default=5, help="Maximum iterations for book generation.")
    args = parser.parse_args()

    if not args.api_key:
       logging.error("API key not provided")
       return

    input_prompt = get_input()
    logging.info(f"Initial Input: {input_prompt}\n")
    
    try:
       api = create_api_instance(args.api, args.api_key)
    except ValueError as e:
       logging.error(e)
       return

    # Initialize Agents
    writer = WriterAgent(api)
    reviewer = ReviewerAgent(api)

    # Initialize Exporter
    exporter = PDFExporter()

    # Initialize Filter
    filter = Filter(threshold=7)

    log_filename = "review_log.txt"
    
    for epoch in range(args.max_iterations):
        logging.info(f"\n--- Epoch {epoch + 1} ---")
        
        book, score, feedback = await generate_and_review(writer, reviewer, input_prompt, log_filename, exporter, filter, epoch)
        
        if not book:
            continue
    
        # Filter and Export
        if filter.is_approved(score):
            logging.info("Book approved!")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            final_filename = f"book_final_{timestamp}.txt"
            exporter.export(book, final_filename)
            logging.info(f"Book exported to {exporter.output_dir}/{final_filename}")
            break # Stop iterating if the book has been approved
        else:
             logging.info("Book not approved, iterating ...")
                # Adjust input prompt based on feedback for the next iteration
             input_prompt = f"Improve the previous book. Previous feedback was: {feedback}"

    logging.info("\nBook generation process finished.")

if __name__ == "__main__":
    asyncio.run(main())