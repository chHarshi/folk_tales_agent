from agents.coordinator import CoordinatorAgent

def main():
    agent = CoordinatorAgent()

    print("=" * 50)
    print("🇮🇳 Indian Folk Tales Agent")
    print("=" * 50)

    query = input(" Enter your query: ")

    print("\nChoose narration language:")
    print("1. English")
    print("2. Hindi")
    print("3. Telugu")

    lang_choice = input("Enter choice (1/2/3): ")

    lang_map = {
        "1": "en",
        "2": "hi",
        "3": "te"
    }
    language = lang_map.get(lang_choice, "en")

    image_choice = input(" Do you want an image? (y/n): ").lower().strip()
    do_image = image_choice == "y"

    outputs = agent.handle_query(
        query=query,
        language=language,
        do_tts=True,
        do_image=do_image
    )

    print("\n--------------------")
    print(" STORY OUTPUT")
    print("--------------------")
    print(outputs["story"])

    if outputs["audio"]:
        print("\n Audio narration generated")

    if outputs["image"]:
        print(" Image generated")
    else:
        print(" Image not requested")

if __name__ == "__main__":
    main()
