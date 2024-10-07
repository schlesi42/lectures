import random
def spin_the_wheel(participants: list[str]) -> str:
    return random.choice(participants)

if __name__ == '__main__':
    participants = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    print(spin_the_wheel(participants))