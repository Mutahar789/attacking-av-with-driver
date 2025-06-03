# CS205 Project

Scripts for creating CARLA simulations

## Running `pcla_drive.py`

- To run `pcla_drive.py`, either:
  - Copy the script into the `PCLA` folder, **OR**
  - Add the `PCLA` folder to your `PYTHONPATH`

## Setup

### Guides followed

**Primary:**

- [CARLA Build on Windows (Official)](https://carla.readthedocs.io/en/0.9.13/build_windows/#unreal-engine)
- [Installing DReyeVR on CARLA 0.9.13 (Medium)](https://medium.com/@ailene.chan/the-struggle-is-real-installing-dreyevr-carla-0-9-13-d68d0d1cd625)

**Also helpful:**

- [Installing DReyeVR on CARLA 0.9.13 on Windows 11 (Medium)](https://medium.com/@ailene.chan/the-struggle-is-real-installing-dreyevr-carla-0-9-13-simulator-unrealengine-4-26-on-windows-11-eb5bee1353e7)
- [CARLA Fixes Repo](https://github.com/chanyca/carla_fixes/tree/main)
- [CARLA Dev Branch](https://github.com/carla-simulator/carla/tree/ue4-dev#)
- [DReyeVR Install Docs](https://github.com/HARPLab/DReyeVR/blob/main/Docs/Install.md)

## DReyeVR fork:
https://github.com/Mutahar789/DReyeVR

Using this fork will allow you to allow the vehicle.apply_control function to work on Ego Vehicle. Use this if you plan to integrate any model (e.g., vision-based) for driving task.

## Additional Setup Steps

1. In `carla/Unreal/CarlaUE4/CarlaUE4.Build.cs`, set:
    - `UseSRanipalPlugin = false;`  *(For HTC Vive Eye Tracking - disable if not used)*
    - `UseLogitechPlugin = false;`  *(For Logitech wheel/pedal set - disable if not used)*

2. In `carla/Util/ContentUtil.py`:
    - Change the **assets download URL** from `http` → `https` (to avoid download errors).

## Notes on Building PythonAPI

- After DReyeVR setup, running `make PythonAPI` may cause extraction errors for `xerces-c-3.2.3` (because we manually downloaded and placed it in the `Build` directory).  
→ **These errors can be safely ignored.**

- Install required build tools:

```bash
pip install wheel
```

## Building and Installing CARLA Python API

```bash
make LibCarla

cd PythonAPI/carla

python setup.py bdist_egg bdist_wheel

# Install the built wheel
pip install dist/<path to .whl file>
```

**IMPORTANT:** You must install this built .whl both:

1. In your system Python installation
2. In any Conda environment you are using

## Running DReyeVR

Once you have built the shipping package, run CARLA with DReyeVR as:

```bash
# Navigate to built shipping directory
cd \PATH\TO\CARLA\Build\UE4Carla\0.9.13-dirty\WindowsNoEditor\

# Launch in VR mode
CarlaUE4.exe -vr

# Optional for performance:
CarlaUE4.exe -vr -quality-level=Low
```

**Notes:**

- -quality-level=Low → boosts framerate without much loss of visual fidelity
- You can also run without VR:

```bash
CarlaUE4.exe
```

This launches flat-screen Carla with DReyeVR features still enabled.

## Useful Tips

1. The DReyeVR Ego vehicle is NOT the same as a standard CARLA vehicle type (when built with vanilla CARLA API). You must use the built Python API .whl corresponding to your DReyeVR build — not the official CARLA release.
2. **Freeing the CARLA port (2000)**: If CARLA was not closed cleanly, port 2000 might be stuck: 
```bash
netstat -ano | findstr 2000

# Find the PID and kill it (example PID 68876)
taskkill /PID 68876 /F
```

## Using PCLA Agent with DReyeVR

The PCLA agent allows you to drive the DReyeVR Ego vehicle. Use these forks for best Windows compatibility:
- DReyeVR fork:
https://github.com/Mutahar789/DReyeVR

- PCLA fork (for Windows):
https://github.com/Mutahar789/PCLA
