import carla
import random
import time
from PCLA import PCLA, route_maker, location_to_waypoint

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world('Town02')
    blueprint_library = world.get_blueprint_library()

    spawn_points = world.get_map().get_spawn_points()
    if len(spawn_points) < 2:
        print("Not enough spawn points available.")
        return

    start_point, end_point = random.sample(spawn_points, 2)

    ego_vehicle = None
    for actor in world.get_actors().filter('*vehicle*'):
        if 'dreyevr_vehicle' in actor.type_id:
            ego_vehicle = actor
            break

    if ego_vehicle is None:
        print("Ego vehicle not found.")
        return

    print(f"Ego vehicle: {ego_vehicle.type_id} (id {ego_vehicle.id})")

    waypoints = location_to_waypoint(client, start_point.location, end_point.location)
    route_file = 'random_route.xml'
    route_maker(waypoints, route_file)

    agent_name = 'neat_neat'
    pcla_agent = PCLA(agent_name, ego_vehicle, route_file, client)

    ego_vehicle.set_autopilot(False)
    print("Autopilot OFF — External control enabled (if DReyeVR allows it)")

    try:
        while True:
            control = pcla_agent.get_action()
            print(f"PCLA Control: {control}")
            ego_vehicle.apply_control(control)
            world.tick()
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass

    finally:
        pcla_agent.cleanup()
        print("Simulation ended.")

if __name__ == '__main__':
    main()