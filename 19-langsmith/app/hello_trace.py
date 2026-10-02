from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable

@traceable
def detect_topic(question: str) -> str:
    q = question.lower()

    if "fee" in q:
        return "fees"
    elif "limit" in q:
        return "limits"
    elif "lost" in q:
        return "lost_card"
    return "other"

if __name__ == "__main__":
    print(detect_topic("hello world"))
    print(detect_topic("card is lost?"))
    print(detect_topic("what is the limitation of your card?"))