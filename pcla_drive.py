import carla
import random
import time
from PCLA import PCLA, route_maker, location_to_waypoint
import datetime

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world('Town02')
    blueprint_library = world.get_blueprint_library()

    # Retrieve spawn points
    spawn_points = world.get_map().get_spawn_points()
    if len(spawn_points) < 2:
        print("Not enough spawn points available.")
        return

    # Randomly select start and end points
    start_point, end_point = random.sample(spawn_points, 2)

    # Find DReyeVR ego vehicle
    ego_vehicle = None
    for actor in world.get_actors().filter('*vehicle*'):
        if 'dreyevr_vehicle' in actor.type_id:
            ego_vehicle = actor
            break

    if ego_vehicle is None:
        print("Ego vehicle not found.")
        return

    print(f"Ego vehicle: {ego_vehicle.type_id} (id {ego_vehicle.id})")

    # Generate route
    ego_vehicle.set_transform(start_point)
    waypoints = location_to_waypoint(client, start_point.location, end_point.location)
    route_file = 'random_route.xml'
    route_maker(waypoints, route_file)

    # Initialize PCLA agent
    agent_name = 'tfpp_l6_0'
    pcla_agent = PCLA(agent_name, ego_vehicle, route_file, client)

    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    ego_vehicle.set_autopilot(False)

    try:
        while True:
            control = pcla_agent.get_action()
            ego_vehicle.apply_control(control)
            world.tick()

    finally:
        pcla_agent.cleanup()
        print("Simulation ended.")

if __name__ == '__main__':
    main()
