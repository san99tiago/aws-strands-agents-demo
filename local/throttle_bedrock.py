import subprocess
import threading
import time


def run_script_1():
    subprocess.run(
        [
            "../.venv/bin/python",
            "/Users/santigrc/Desktop/programming/aws-strands-agents-demo/local/ex_00_hello_world.py",
        ]
    )


def run_script_2():
    subprocess.run(
        [
            "../.venv/bin/python",
            "/Users/santigrc/Desktop/programming/aws-strands-agents-demo/local/ex_01_select_model.py",
        ]
    )


def main():
    while True:
        threads = []
        for _ in range(100):
            thread = threading.Thread(target=run_script_1)
            thread = threading.Thread(target=run_script_2)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        time.sleep(0.01)


if __name__ == "__main__":
    main()
