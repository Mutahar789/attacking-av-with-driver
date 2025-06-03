import carla
import random
import time
import threading
from pynput import keyboard

TRAFFIC_VEHICLES = 30

client = carla.Client('169.234.62.58', 2000)
client.set_timeout(10.0)
world = client.load_world('Town06')
world = client.get_world()
blueprint_library = world.get_blueprint_library()
map = world.get_map()
traffic_manager = client.get_trafficmanager()

ego_vehicle = None
for actor in world.get_actors().filter('*vehicle*'):
    if 'dreyevr_vehicle' in actor.type_id:
        ego_vehicle = actor
        break

if ego_vehicle is None:
    print("Ego vehicle not found.")
    exit()

print(f"Ego vehicle: {ego_vehicle.type_id} (id {ego_vehicle.id})")

print(actor.type_id)
print(isinstance(actor, carla.Vehicle))

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

autopilot_enabled = True
ego_vehicle.set_autopilot(True, traffic_manager.get_port())
print("Ego vehicle: Autopilot ON")

def on_press(key):
    global autopilot_enabled

    try:
        if key.char.lower() in ['w', 'a', 's', 'd', ' ']:
            if autopilot_enabled:
                ego_vehicle.set_autopilot(False)
                autopilot_enabled = False
                print(f"[{round(time.time(), 1)}s] User took control -> Autopilot OFF")

        elif key.char.lower() == "p":
            if not autopilot_enabled:
                ego_vehicle.set_autopilot(True, traffic_manager.get_port())
                autopilot_enabled = True
                print(f"[{round(time.time(), 1)}s] Manual -> Autopilot ON (via F3)")

    except AttributeError:
        if key == keyboard.Key.up or key == keyboard.Key.down or key == keyboard.Key.left or key == keyboard.Key.right:
            if autopilot_enabled:
                ego_vehicle.set_autopilot(False)
                autopilot_enabled = False
                print(f"[{round(time.time(), 1)}s] User took control -> Autopilot OFF")


listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
    while True:
        world.tick()
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    print("Cleaning up traffic...")
    for v in traffic_vehicles:
        v.destroy()
    print("Done.")