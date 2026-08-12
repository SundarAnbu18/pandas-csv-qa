"""The AI part, kept separate from Django on purpose.

Views should stay small and only deal with web things (request in, page out).
Anything that talks to Claude lives here, so you can test it on its own.
"""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import CSVLoader
from langchain_core.prompts import PromptTemplate

from docs.employee_data import employees

PROMPT = PromptTemplate(
    template=(
        "Use this employee data to answer.\n\n{context}\n\n"
        "Question: {question}"
    ),
    input_variables=["context", "question"],
)


@lru_cache(maxsize=1)
def _load_context(csv_file):
    """Read the CSV once and remember it.

    lru_cache means the file is only read on the first question. Every later
    question reuses the same text instead of hitting the disk again.
    """
    documents = CSVLoader(file_path=csv_file).load()
    return "\n".join(doc.page_content for doc in documents)


def _reply_to_text(reply):
    """Pull the plain answer out of Claude's reply.

    Usually reply.content is just a string. But newer models can send back a
    list of blocks instead, like [{"type": "thinking", ...}, {"type": "text",
    "text": "Steven King..."}]. We only want the "text" blocks.
    """
    content = reply.content
    if isinstance(content, str):
        return content.strip()

    parts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "\n".join(part for part in parts if part).strip()


def answer_question_from_csv(question, csv_file=employees):
    """Send the CSV plus the question to Claude and return the reply text."""
    model = ChatAnthropic(model="claude-sonnet-5")
    chain = PROMPT | model
    reply = chain.invoke({"context": _load_context(csv_file), "question": question})
    return _reply_to_text(reply)
