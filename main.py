from src.crypto import Crypto


def main():
    generator = Crypto()
    print(generator.generateXVersion("dbd54102-1882-4cd3-b434-633e5bc5468d", "1737093668932"))


if __name__ == "__main__":
    main()
