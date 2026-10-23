def load_user():
    return None


def greet():
    user = load_user()
    return user["name"]


if __name__ == "__main__":
    greet()
