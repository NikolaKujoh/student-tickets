# Student tickets

Small app for selling student tickets: index (`bbbb/gggg`), faculty, day (1–4). One ticket per student per day.

## Run it (Windows, no Python needed)

1. Download `tickets.exe` from the [latest release](https://github.com/NikolaKujoh/student-tickets/releases/latest).
2. Put it in its own folder (e.g. `Desktop\tickets`).
3. Double-click it. If Windows shows "Windows protected your PC", click **More info → Run anyway**.

All sales are saved in `tickets.db`, created next to `tickets.exe`. Back up that file; delete it to start fresh.

## Run from source (any OS with Python 3)

```
python tickets.py
```

Linux may need `sudo apt install python3-tk` first.

## New exe release

```
git tag v1.0.1
git push origin v1.0.1
```

GitHub Actions builds `tickets.exe` and attaches it to the release.
