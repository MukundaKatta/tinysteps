"""CLI for tinysteps."""
import sys, json, argparse
from .core import Tinysteps

def main():
    parser = argparse.ArgumentParser(description="TinySteps — Baby Milestone Tracker. AI-powered developmental milestone tracking and early concern detection.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Tinysteps()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.detect(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"tinysteps v0.1.0 — TinySteps — Baby Milestone Tracker. AI-powered developmental milestone tracking and early concern detection.")

if __name__ == "__main__":
    main()
