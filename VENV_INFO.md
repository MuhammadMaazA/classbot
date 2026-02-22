# Virtual Environment Setup

All Python packages are installed in an isolated virtual environment at `~/classroom_env/` to avoid conflicts with system packages.

## First Time Setup

```bash
cd ~/classroom_ai
bash setup.sh
```

This will:
1. Create virtual environment at `~/classroom_env/` directory
2. Install all required Python packages (insightface, opencv-python, etc.)
3. Keep your system Python clean

## Running the System

The `run.sh` script automatically activates the venv:

```bash
bash run.sh
```

## Manual venv Usage

If you want to run Python scripts manually:

```bash
# Activate venv
source ~/classroom_env/bin/activate

# Now you can run any script
python3 classroom_monitor_picam.py
python3 test_camera.py

# Deactivate when done
deactivate
```

## Installing Additional Packages

```bash
source ~/classroom_env/bin/activate
pip install package_name
```

## Checking What's Installed

```bash
source ~/classroom_env/bin/activate
pip list
```

## Benefits of venv

✓ **Isolated**: Packages don't interfere with system Python
✓ **Clean**: Easy to delete and recreate (`rm -rf ~/classroom_env`)
✓ **Portable**: Can have different versions per project
✓ **No sudo**: No need for `--break-system-packages` flag

## Troubleshooting

### "venv not found" error

Run setup:
```bash
bash setup.sh
```

### Packages not found when running script

Make sure to activate venv first:
```bash
source ~/classroom_env/bin/activate
python3 your_script.py
```

Or just use:
```bash
bash run.sh  # This activates venv automatically
```

### Want to start fresh?

```bash
rm -rf ~/classroom_env
bash setup.sh
```
