import carla
import random
import time
import threading
from pynput import keyboard
from carla import Vector3D, Color

TM_SEED=20
SIM_SEED = 20
TM_SEEDS = [20]

random.seed(SIM_SEED)
TRAFFIC_VEHICLES = 30

stop_signs_to_patch = {
    (round(42.729271, 1), round(136.699997, 1), round(0.038605, 1))
}

start_point = carla.Transform(carla.Location(x=111.80159759521484, y=1.9382578134536743, z=0.00991920568048954), carla.Rotation(pitch=0.2358054369688034, yaw=-1.162109375, roll=-0.0257568322122097))

def place_black_patches_on_stop_signs(client, world, map):
    global stop_sign_ids_to_patch
    stop_signs = map.get_all_landmarks_of_type('206')
    for lm in stop_signs:
        loc = lm.transform.location
        loc_key = (round(loc.x, 1), round(loc.y, 1), round(loc.z, 1))
        if loc_key in stop_signs_to_patch:
            print('here')
            transform = lm.transform
            rot = transform.rotation

            forward_vector = transform.get_forward_vector()
            patch_location = transform.location - forward_vector * 0.15
            patch_location.z += 2.2
            box = carla.BoundingBox(patch_location, Vector3D(0.001, 0.2, 0.2))

            world.debug.draw_box(
                box,
                rot,
                thickness=0.1,
                color=Color(0, 0, 0),
                life_time=0, 
                persistent_lines=True
            )

            box = carla.BoundingBox(patch_location, Vector3D(0.001, 0.1, 0.1))

            world.debug.draw_box(
                box,
                rot,
                thickness=0.1,
                color=Color(0, 0, 0), 
                life_time=0,
                persistent_lines=True
            )

client = carla.Client('169.234.62.58', 2000)
client.set_timeout(10.0)
world = client.load_world('Town05')
world.set_weather(carla.WeatherParameters.ClearNoon)
world = client.get_world()
blueprint_library = world.get_blueprint_library()
map = world.get_map()
traffic_manager = client.get_trafficmanager()
settings = world.get_settings()
settings.synchronous_mode = True
settings.fixed_delta_seconds = 0.01
world.apply_settings(settings)
traffic_manager.set_random_device_seed(TM_SEED) 

ego_vehicle = None
for actor in world.get_actors().filter('*vehicle*'):
    if 'dreyevr_vehicle' in actor.type_id:
        ego_vehicle = actor
        break

if ego_vehicle is None:
    print("Ego vehicle not found.")
    exit()

print(f"Ego vehicle: {ego_vehicle.type_id} (id {ego_vehicle.id})")

spawn_points = map.get_spawn_points()
random.shuffle(spawn_points)
traffic_vehicles = []

for _ in range(TRAFFIC_VEHICLES):
    bp = random.choice(blueprint_library.filter('vehicle.*'))
    spawn_point = spawn_points.pop(0)
    npc = world.try_spawn_actor(bp, spawn_point)
    if npc:
        npc.set_autopilot(True)
        traffic_vehicles.append(npc)

print(f"Spawned {len(traffic_vehicles)} traffic vehicles.")

ego_vehicle.set_python_control_active(False)

ego_vehicle.set_transform(start_point)

place_black_patches_on_stop_signs(client, world, map)

autopilot_enabled = True
ego_vehicle.set_autopilot(True, traffic_manager.get_port())

start_time = time.time()
ignore_applied = False

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
        if not ignore_applied and time.time() - start_time > 15:
            traffic_manager.ignore_signs_percentage(ego_vehicle, 100.0)
            print(f"[{round(time.time() - start_time, 1)}s] Ignoring stop signs from now.")
            ignore_applied = True

except KeyboardInterrupt:
    print("Exiting...")

finally:
    print("Cleaning up traffic...")
    for v in traffic_vehicles:
        v.destroy()
    print("Done.")
