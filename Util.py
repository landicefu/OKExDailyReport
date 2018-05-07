
def read_all(path: str, strip: bool = True) -> str:
    with open(path, 'r') as file:
        content = file.read()
    if strip:
        return content.strip()
    else:
        return content
