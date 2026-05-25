import sys
from agent import run_agent

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py \"your questions\"", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    print(f"User: { question}")

    answer = run_agent(question)

    print(f"\n{'=' * 60}")
    print("Final answer")
    print(answer)


if __name__ == '__main__':
    main()