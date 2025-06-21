import carla
import time
import math

def distance(loc1, loc2):
    return math.sqrt(
        (loc1.x - loc2.x) ** 2 +
        (loc1.y - loc2.y) ** 2 +
        (loc1.z - loc2.z) ** 2
    )

def log_and_mark_nearest_stop_sign(client, max_distance=25.0):
    world = client.get_world()
    map = world.get_map()

    ego_vehicle = None
    for actor in world.get_actors().filter('*vehicle*'):
        if 'dreyevr_vehicle' in actor.type_id:
            ego_vehicle = actor
            break

    if not ego_vehicle:
        print("Ego vehicle not found.")
        return

    print(f"Ego vehicle ID: {ego_vehicle.id}")
    stop_signs = map.get_all_landmarks_of_type('206')

    try:
        while True:
            ego_loc = ego_vehicle.get_location()

            nearest_sign = None
            min_dist = float('inf')

            for sign in stop_signs:
                sign_loc = sign.transform.location
                dist = distance(ego_loc, sign_loc)

                if dist < min_dist and dist < max_distance:
                    min_dist = dist
                    nearest_sign = sign

            if nearest_sign:
                loc = nearest_sign.transform.location
                rot = nearest_sign.transform.rotation
                forward = nearest_sign.transform.get_forward_vector()
                patch_loc = loc - forward * 0.15
                patch_loc.z += 2.2

                extent = carla.Vector3D(0.001, 0.2, 0.2)
                box = carla.BoundingBox(patch_loc, extent)

                world.debug.draw_box(
                    box,
                    rot,
                    thickness=0.1,
                    color=carla.Color(0, 0, 0),
                    life_time=0.6, 
                    persistent_lines=False
                )

                print(f"NEAREST STOP SIGN: id={nearest_sign.id}, dist={min_dist:.2f}m")
                print(nearest_sign.transform.location)

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == '__main__':
    client = carla.Client('localhost', 2000) 
    client.set_timeout(10.0)
    log_and_mark_nearest_stop_sign(client)
