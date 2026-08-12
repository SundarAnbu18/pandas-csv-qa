"""Command-line version of the same question-answering, for quick tests.

The real logic now lives in chat/ai.py so that both this script and the Django
web page use exactly the same code.

    python lauch.py
    python lauch.py "How many employees are in department 50?"
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from chat.ai import answer_question_from_csv  # noqa: E402  (must come after load_dotenv)

DEFAULT_QUESTION = "What is the name of the employee with the highest salary?"


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUESTION
    print(answer_question_from_csv(question))


# Only runs when you type `python lauch.py` — not when another file imports this.
if __name__ == "__main__":
    main()
