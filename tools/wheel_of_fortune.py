import random
def spin_the_wheel(participants: list[str]) -> str:
    return random.choice(participants)

if __name__ == '__main__':
    participants = ['Michele', 'Michael', 'Tim', 'Marvin']
    print(spin_the_wheel(participants))