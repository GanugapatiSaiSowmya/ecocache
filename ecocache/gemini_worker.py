import sys
import os

def main():
    api_key = sys.argv[1]
    prompt_arg = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gemma-3-1b-it"
    use_file = "--file" in sys.argv

    if use_file:
        with open(prompt_arg, 'r') as f:
            prompt = f.read()
    else:
        prompt = prompt_arg

    # Disable all parallelism to avoid fork conflicts
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"

    from google import genai
    client = genai.Client(api_key=api_key)
    result = client.models.generate_content(model=model, contents=prompt)
    print(result.text, end="")

if __name__ == "__main__":
    main()