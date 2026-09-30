from dotenv import load_dotenv
load_dotenv()
from agents.coordinator import CoordinatorAgent

def main():
    agent = CoordinatorAgent()

    print("=" * 50)
    print("Indian Folk Tales Agent")
    print("=" * 50)

    query = input("Enter your query: ")

    print("\nChoose narration language:")
    print("1. English  2. Hindi  3. Telugu")
    lang_choice = input("Enter choice (1/2/3): ")
    language = {"1": "en", "2": "hi", "3": "te"}.get(lang_choice, "en")

    do_image = input("Do you want an image? (y/n): ").lower().strip() == "y"

    import time
    t0 = time.time()
    result = agent.handle_query(query, language, do_tts=True, do_image=do_image)
    print(f"\n[TIMING] handle_query took {time.time() - t0:.1f} seconds")

    print("\n--- STORY ---")
    print(result["story"])

    if result["found"]:
        for s in result["sources"]:
            print(f"\nSource: {s['title']} ({s['region']}) — {s['source']}")
        if result["audio"]:
            print(f"\nAudio saved to: {result['audio']}")
        if result["image"]:
            print(f"Image saved to: {result['image']}")
        if result["validation"]:
            print(f"\nValidation: {result['validation']}")

if __name__ == "__main__":
    main()