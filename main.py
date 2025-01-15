# main.py
from agents.writer.writer_agent import WriterAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from api.openai_api import OpenAIAPI
from api.google_api import GoogleAPI
from api.mock_api import MockAPI
from exporter import PDFExporter
from filter import Filter
import random
import time
import argparse
import os
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_input():
    """
    Gets the user input or generates random input if the user chooses.

    Returns:
        str: The user input or a random input.
    """
    use_random = input("Generate random input? (yes/no): ").lower() == "yes"
    if use_random:
        input_options = [
            "A fantasy adventure in a magical kingdom",
            "A sci-fi thriller on a space station",
            "A mystery in a haunted house",
            "A romance between a detective and a suspect",
        ]
        return random.choice(input_options)
    else:
        return input("Enter the book's theme: ")


def create_api_instance(api_type, api_key):
    if api_type == "openai":
        return OpenAIAPI(api_key=api_key)
    elif api_type == "google":
        return GoogleAPI(api_key=api_key)
    elif api_type == "mock":
        return MockAPI(api_key=api_key)
    else:
        raise ValueError(f"Invalid API type: {api_type}")


async def generate_book(
    writer, book, review, input_prompt, log_filename, exporter, epoch
):
    """
    Generates and reviews a book, with a timeout for API calls.

    Args:
        writer: Writer agent responsible for generating the book.
        book: The current book iteration. Book is None in the first.
        feedback: Feedback from the current book iteration. feedback is None in the first.
        input_prompt: The prompt for the writer agent.
        log_filename: Path to the log file.
        exporter: Exporter instance for saving books.
        epoch: Current iteration or epoch.

    Returns:
        tuple: Generated book, review score, and feedback.
    """
    try:
        # Generate Book
        book = await writer.generate_book(input_prompt, book, review)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        book_filename = f"book_{timestamp}_epoch{epoch + 1}.txt"

        # Save book content
        book_path = os.path.join(exporter.output_dir, book_filename)
        with open(book_path, "w", encoding="utf-8") as file:
            file.write(book)
        logging.info(f"Book content saved to: {book_path}")
        return book

    except Exception as e:
        error_message = f"An error occurred during iteration {epoch + 1}: {e}"
        logging.error(error_message)

        # Log error to review log
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(f"Epoch: {epoch + 1}, Error: {error_message}\n")

        return None, 0, error_message


async def review_book(reviewer, book, input_prompt, log_filename, exporter, epoch):
    """
    Generates and reviews a book, with a timeout for API calls.

    Args:
        reviewer: Reviewer agent responsible for reviewing the book.
        input_prompt: The prompt for the writer agent.
        log_filename: Path to the log file.
        exporter: Exporter instance for saving books.
        epoch: Current iteration or epoch.

    Returns:
        tuple: Generated book, review score, and feedback.
    """
    try:
        # Review Book
        review = await reviewer.review_book(book, input_prompt)
        review_parsed = reviewer.parse_review(review)
        score = review_parsed.get("overall_score", 0)
        score_cat = review_parsed.get("categories", 0)
        feedback = review_parsed.get("feedback", "No feedback provided")

        # Log review
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                f"Epoch: {epoch + 1}, Score: {score}, Score Categories: {score_cat}, Feedback: {feedback}\n"
            )

        logging.info(f"Review Score: {score}")
        return review, score, feedback

    except Exception as e:
        error_message = f"An error occurred during iteration {epoch + 1}: {e}"
        logging.error(error_message)

        # Log error to review log
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(f"Epoch: {epoch + 1}, Error: {error_message}\n")

        return None, 0, error_message


async def main():
    """
    Main function to run the AI book generator.
    """
    parser = argparse.ArgumentParser(description="AI Book Generator")
    parser.add_argument(
        "--api",
        type=str,
        default="google",
        choices=["openai", "google", "mock"],
        help="API to use (openai, google)",
    )
    parser.add_argument("--api_key", type=str, help="API key for the selected API")
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=5,
        help="Maximum iterations for book generation.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info("Starting AI Book Generator...")

    input_prompt = get_input()
    logging.info(f"Initial Input: {input_prompt}\n")

    try:
        api = create_api_instance(args.api, args.api_key)
    except ValueError as e:
        logging.error(f"Failed to create API instance: {e}")
        return

    # Initialize agents and tools
    writer = WriterAgent(api)
    reviewer = ReviewerAgent(api)
    exporter = PDFExporter()
    filter = Filter(threshold=86)

    log_filename = "review_log.txt"

    previous_books = [None, None]
    previous_reviews = [None, None]

    approved = False
    book = None
    score = None
    best_score = 0
    review = None
    for epoch in range(args.max_iterations):
        logging.info(f"\n--- Epoch {epoch + 1} ---")
        try:
            generate_book
            # Generate and review the book
            book = await generate_book(
                writer,
                previous_books,
                previous_reviews,
                input_prompt,
                log_filename,
                exporter,
                epoch,
            )
            # Generate and review the book
            review, score, feedback = await review_book(
                reviewer, book, input_prompt, log_filename, exporter, epoch
            )
            if not book:
                logging.warning("No book generated, skipping this iteration.")
                continue

            # Update history with current book and review
            if int(score) > best_score:
                best_score = int(score)
                previous_books[0] = book
                previous_reviews[0] = review

            previous_books[1] = book
            previous_reviews[1] = review

            # Filter and export if approved
            if filter.is_approved(int(score), review):
                logging.info("Book approved!")
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                final_filename = f"book_final_{timestamp}"
                processed_content = exporter.process_book(book)
                exporter.export(processed_content, final_filename)
                logging.info(f"Book exported to {exporter.output_dir}/{final_filename}.pdf")
                break  # Stop iterating if the book is approved

            # Update input prompt with feedback for next iteration
            logging.info(f"Current book score: {score}")
            logging.info("Book not approved, refining prompt for the next iteration...")

        except Exception as e:
            logging.error(f"An error occurred during epoch {epoch + 1}: {e}")
            if approved:
                break
            continue

    logging.info("\nBook generation process finished.")


if __name__ == "__main__":
    asyncio.run(main())
