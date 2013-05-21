from lucy.models.config import Config
from lucy.archive import process


def main():
    obj = Config.load('default')
    process(obj)


if __name__ == "__main__":
    main()
