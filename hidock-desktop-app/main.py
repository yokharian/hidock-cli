from hidock_cli import HiDockCLI

if __name__ == "__main__":
    hidock_cli = HiDockCLI(attempt_auto_connect=True)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nExiting HiDock CLI...")
