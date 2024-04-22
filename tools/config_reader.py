import os

import yaml


class RequiredFields:
    # -------------- project related fields --------------
    project_name = "project_name"
    simulation_time = "simulation_time"
    check_polar_entering = "check_polar_entering"
    # -------------- project related fields --------------
    # -------------- constellation related fields --------------
    constellation_type = "constellation_type"
    orbit_number = "orbit_number"
    sat_per_orbit = "sat_per_orbit"
    inclination = "inclination"
    starting_phase = "starting_phase"
    altitude = "altitude"
    satellite_gsl_interface_number = "satellite_gsl_interface_number"
    # -------------- constellation related fields --------------
    # -------------- routing protocol field --------------
    routing_protocol = "routing_protocol"
    # -------------- routing protocol field --------------
    # -------------- lipsin apps --------------
    lipsin_apps = "lipsin_apps"
    ground_stations = "ground_stations"
    # -------------- lipsin apps --------------


class ConfigReader:
    def __init__(self):
        # ---------- project related questions ----------
        self.project_name = None
        self.simulation_time = None
        self.check_polar_entering = None
        # ---------- project related questions ----------
        # ---------- constellation related questions ----------
        self.constellation_type = None
        self.orbit_number = None
        self.sat_per_orbit = None
        self.inclination = None
        self.starting_phase = None
        self.altitude = None
        self.satellite_gsl_interface_number = None
        # ---------- constellation related questions ----------
        # ---------- link questions ----------
        self.isl_link_bandwidth = None
        self.gsl_link_bandwidth = None
        # ---------- link questions ----------
        # ---------- routing protocol questions ----------
        self.routing_protocols = None
        # ---------- routing protocol questions ----------
        # ---------- lipsin apps ----------
        self.lipsin_apps = None
        # ---------- lipsin apps ----------

    def load(self, configuration_file_path: str = "../resources/constellation_config.yml",
             selected_config: str = "default"):
        with open(file=configuration_file_path, mode='r', encoding="utf-8") as f:
            selected_config_data = yaml.load(stream=f, Loader=yaml.FullLoader).get(selected_config, None)
            if selected_config_data is not None:
                # --- project related ---
                self.project_name = selected_config_data.get(RequiredFields.project_name, None)
                self.simulation_time = selected_config_data.get(RequiredFields.simulation_time, None)
                self.check_polar_entering = selected_config_data.get(RequiredFields.check_polar_entering, None)
                # --- project related ---
                # --- constellation related ---
                self.constellation_type = (selected_config_data.get(RequiredFields.constellation_type), None)
                self.orbit_number = int(selected_config_data.get(RequiredFields.orbit_number, None))
                self.sat_per_orbit = int(selected_config_data.get(RequiredFields.sat_per_orbit, None))
                self.inclination = int(selected_config_data.get(RequiredFields.inclination, None))
                self.starting_phase = int(selected_config_data.get(RequiredFields.starting_phase, None))
                self.altitude = int(selected_config_data.get(RequiredFields.altitude, None))
                self.satellite_gsl_interface_number = int(selected_config_data.get(RequiredFields.satellite_gsl_interface_number, None))
                # --- constellation related ---
                # --- routing protocol ---
                self.routing_protocols = selected_config_data.get(RequiredFields.routing_protocol, None)
                # --- routing protocol ---
                # --- lipsin app ---
                self.lipsin_apps = selected_config_data.get(RequiredFields.routing_protocol, None)
                # --- lipsin app ---


if __name__ == "__main__":
    import sys

    sys.path.append("../")
    config_reader = ConfigReader()
    config_reader.load()
    print(os.path.abspath(os.curdir))
