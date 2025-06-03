import carla
import random
import time
import threading
from pynput import keyboard

# === CONFIG ===
INPUT_TIMEOUT = 2.0  # seconds
TRAFFIC_VEHICLES = 30

# === Connect ===
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
blueprint_library = world.get_blueprint_library()
map = world.get_map()
traffic_manager = client.get_trafficmanager()

# === Find Ego Vehicle ===
ego_vehicle = None
for actor in world.get_actors().filter('*vehicle*'):
    if 'dreyevr_vehicle' in actor.type_id:
        ego_vehicle = actor
        break

if ego_vehicle is None:
    print("Ego vehicle not found.")
    exit()

print(f"Ego vehicle: {ego_vehicle.type_id} (id {ego_vehicle.id})")

# === Spawn traffic ===
spawn_points = map.get_spawn_points()
traffic_vehicles = []

for _ in range(TRAFFIC_VEHICLES):
    bp = random.choice(blueprint_library.filter('vehicle.*'))
    spawn_point = random.choice(spawn_points)
    npc = world.try_spawn_actor(bp, spawn_point)
    if npc:
        npc.set_autopilot(True, traffic_manager.get_port())
        traffic_vehicles.append(npc)

print(f"Spawned {len(traffic_vehicles)} traffic vehicles.")

# === Autopilot switching logic ===
last_input_time = time.time()
autopilot_enabled = True
ego_vehicle.set_autopilot(True, traffic_manager.get_port())
print("Ego vehicle: Autopilot ON")

# === Global keyboard listener ===
def on_press(key):
    global last_input_time, autopilot_enabled

    try:
        if key.char.lower() in ['w', 'a', 's', 'd', ' ']:
            last_input_time = time.time()
            if autopilot_enabled:
                ego_vehicle.set_autopilot(False)
                autopilot_enabled = False
                print(f"[{round(time.time(), 1)}s] User took control → Autopilot OFF")
    except AttributeError:
        # For special keys
        if key == keyboard.Key.up or key == keyboard.Key.down or key == keyboard.Key.left or key == keyboard.Key.right:
            last_input_time = time.time()
            if autopilot_enabled:
                ego_vehicle.set_autopilot(False)
                autopilot_enabled = False
                print(f"[{round(time.time(), 1)}s] User took control → Autopilot OFF")

listener = keyboard.Listener(on_press=on_press)
listener.start()

# === Main loop ===
try:
    while True:
        world.tick()
        current_time = time.time()

        if not autopilot_enabled and (current_time - last_input_time) > INPUT_TIMEOUT:
            ego_vehicle.set_autopilot(True, traffic_manager.get_port())
            autopilot_enabled = True
            print(f"[{round(current_time, 1)}s] No input for {INPUT_TIMEOUT}s → Autopilot ON")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    print("Cleaning up traffic...")
    for v in traffic_vehicles:
        v.destroy()
    print("Done.")