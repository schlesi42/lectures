#!/usr/bin/env python3
import sys
import random
import os


def read_names_from_file(file_path):
	try:
		with open(file_path, "r", encoding="utf-8") as f:
			lines = f.read().splitlines()
			return [line.strip() for line in lines if line.strip()]
	except FileNotFoundError:
		return []


def resolve_names_file_path():
	# Resolve names.txt relative to the repository root (one level up from this script)
	script_dir = os.path.dirname(os.path.abspath(__file__))
	repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
	return os.path.join(repo_root, "names.txt")


def main():
	names_file = resolve_names_file_path()
	names = read_names_from_file(names_file)

	if not names:
		print(f"No names found. Please create 'names.txt' with one name per line at: {names_file}")
		print("Example:")
		print("Alice\nBob\nCharlie")
		sys.exit(1)

	selection = random.choice(names)
	print(selection)


if __name__ == "__main__":
	main()


