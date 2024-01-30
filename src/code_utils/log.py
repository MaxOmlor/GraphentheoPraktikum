from datetime import datetime
import threading

log_file_path = 'log.txt'
quiet = False
log_lock = threading.Lock()  # Lock zur Synchronisation der Threads

def log(text):
    time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_text = f'[{time_stamp}] {text}'

    try:
        with log_lock:  # Hier verwenden wir den Lock, um den kritischen Abschnitt zu schützen
            with open(log_file_path, 'a+') as log_file:
                log_file.write(log_text + '\n')
                if not quiet:
                    print(log_text)
    except Exception as e:
        print(f'Fehler beim Schreiben der Nachricht "{log_text}" in die Log-Datei: {e}')
