import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class RestartHandler(FileSystemEventHandler):
    def __init__(self, run_cmd):
        self.run_cmd = run_cmd
        self.proc = None
        self.restart()

    def restart(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        self.proc = subprocess.Popen(self.run_cmd)

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected change in {event.src_path}, restarting...")
            self.restart()

if __name__ == "__main__":
    run_cmd = [sys.executable, "-m", "app.main"]
    event_handler = RestartHandler(run_cmd)
    observer = Observer()
    observer.schedule(event_handler, path="app", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    if event_handler.proc:
        event_handler.proc.terminate() 