if __name__ == "__main__":
    import sys

    sys.path.append("../")

import os
import yaml
from modules import ModuleTypes as mtm
from modules import GroundStation as gsm
from applications import LipsinApp as lam
from modules import GslLink as glm
from modules import InterSatelliteLink as islm
from user_input import questions as qm
from PyInquirer import prompt


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
    area_orbit_count = "area_orbit_count"
    area_sat_per_orbit = "area_sat_per_orbit"
    inclination = "inclination"
    starting_phase = "starting_phase"
    altitude = "altitude"
    satellite_gsl_interface_number = "satellite_gsl_interface_number"
    start_to_fail = "start_to_fail"
    # -------------- constellation related fields --------------
    # -------------- link related fields --------------
    isl_link_bandwidth = "isl_link_bandwidth"
    gsl_link_bandwidth = "gsl_link_bandwidth"
    # -------------- link related fields -------------
    # -------------- routing protocol field --------------
    routing_protocol = "routing_protocol"
    hello_interval = "hello_interval"
    router_dead_interval = "router_dead_interval"
    poll_interval = "poll_interval"
    retransmission_interval = "retransmission_interval"
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
        self.area_orbit_count = None
        self.area_sat_per_orbit = None
        self.inclination = None
        self.starting_phase = None
        self.altitude = None
        self.satellite_gsl_interface_number = None
        self.start_to_fail = None
        # ---------- constellation related questions ----------
        # ---------- link questions ----------
        self.isl_link_bandwidth = None
        self.gsl_link_bandwidth = None
        # ---------- link questions ----------
        # ---------- routing protocol questions ----------
        self.routing_protocol = None
        self.hello_interval = None
        self.router_dead_interval = None
        self.poll_interval = None
        self.retransmission_interval = None
        # ---------- routing protocol questions ----------
        # ---------- lipsin apps ----------
        self.lipsin_apps = None
        # ---------- lipsin apps ----------
        # ---------- ground stations ----------
        self.ground_stations = None
        # ---------- ground stations ----------

    def find_available_configuration_ymls(self):
        """
        寻找可以使用的 yml 配置文件
        :return: 可用的 yml 配置文件
        """
        available_configuration_ymls = []
        resources_file_path = "./resources"
        for file in os.listdir(resources_file_path):
            if os.path.isdir(f"./resources/{file}"):
                continue
            else:
                available_configuration_ymls.append(file)
        return available_configuration_ymls

    def start(self):
        """
        让用户选择配置跌启动函数
        """
        question = qm.QUESTION_FOR_CONFIGURATION_FILE
        question[0]["choices"] = self.find_available_configuration_ymls()
        user_selected_configuration_file = prompt(question)["configuration_file"]
        self.load(configuration_file_path=f"./resources/{user_selected_configuration_file}")
        self.print_loaded_info()

    def load(self, configuration_file_path: str = "./resources/constellation_config_lipsin.yml",
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
                self.constellation_type = selected_config_data.get(RequiredFields.constellation_type, None)
                self.constellation_type = mtm.ConstellationType.convert_str_to_constellation_type(
                    self.constellation_type)
                self.orbit_number = int(selected_config_data.get(RequiredFields.orbit_number, None))
                self.sat_per_orbit = int(selected_config_data.get(RequiredFields.sat_per_orbit, None))
                self.area_orbit_count = int(selected_config_data.get(RequiredFields.area_orbit_count, None))
                self.area_sat_per_orbit = int(selected_config_data.get(RequiredFields.area_sat_per_orbit, None))
                self.inclination = int(selected_config_data.get(RequiredFields.inclination, None))
                self.starting_phase = int(selected_config_data.get(RequiredFields.starting_phase, None))
                self.altitude = int(selected_config_data.get(RequiredFields.altitude, None))
                self.satellite_gsl_interface_number = int(
                    selected_config_data.get(RequiredFields.satellite_gsl_interface_number, None))
                self.start_to_fail = int(selected_config_data.get(RequiredFields.start_to_fail, None))
                # --- constellation related ---
                # --- link related ---
                self.isl_link_bandwidth = ConfigReader.resolve_inter_satellite_link_type(
                    selected_config_data.get(RequiredFields.isl_link_bandwidth))
                self.gsl_link_bandwidth = ConfigReader.resolve_ground_satellite_link_type(
                    selected_config_data.get(RequiredFields.gsl_link_bandwidth))
                # --- link related ---
                # --- routing protocol ---
                self.routing_protocol = selected_config_data.get(RequiredFields.routing_protocol, None)
                self.routing_protocol = mtm.RoutingProtocols.convert_str_to_routing_protocol(self.routing_protocol)
                self.hello_interval = int(selected_config_data.get(RequiredFields.hello_interval, None))
                self.router_dead_interval = int(selected_config_data.get(RequiredFields.router_dead_interval, None))
                self.poll_interval = int(selected_config_data.get(RequiredFields.poll_interval, None))
                self.retransmission_interval = int(selected_config_data.get(RequiredFields.retransmission_interval, None))
                # --- routing protocol ---
                # --- lipsin app ---
                self.lipsin_apps = ConfigReader.resolve_lipsin_apps(
                    selected_config_data.get(RequiredFields.lipsin_apps, None))
                # --- lipsin app ---
                # --- ground stations ---
                self.ground_stations = ConfigReader.resolve_ground_stations(
                    selected_config_data.get(RequiredFields.ground_stations, None))
                # --- ground stations ---

    @classmethod
    def resolve_inter_satellite_link_type(cls, inter_satellite_link_type_str):
        return islm.InterSatelliteLink.convert_str_to_bandwidth(inter_satellite_link_type_str)

    @classmethod
    def resolve_ground_satellite_link_type(cls, ground_satellite_link_type_str):
        return glm.GslLink.convert_str_to_bandwidth(ground_satellite_link_type_str)

    @classmethod
    def resolve_ground_stations(cls, ground_stations_str_list):
        ground_stations = []
        if ground_stations_str_list[0] is None:
            return ground_stations
        for item in ground_stations_str_list:
            name, longitude, latitude = item.split("|")
            longitude = float(longitude)
            latitude = float(latitude)
            ground_station = gsm.GroundStation(name=name, longitude=longitude, latitude=latitude)
            ground_stations.append(ground_station)
        return ground_stations

    @classmethod
    def resolve_lipsin_apps(cls, lipsin_apps_str_list):
        # print(lipsin_apps_str_list)
        lipsin_apps = []
        if lipsin_apps_str_list[0] is None:
            return lipsin_apps
        for item in lipsin_apps_str_list:
            source, *destinations = item.split("|")
            source = int(source)
            destinations = [int(item) for item in destinations]
            lipsin_app = lam.LipsinApp(source=source, destinations=destinations)
            lipsin_apps.append(lipsin_app)
        # print(lipsin_apps)
        return lipsin_apps

    def print_loaded_info(self):
        print_format_string = f"""
        ===================== project_related_fields =====================
        {RequiredFields.project_name}: {self.project_name}
        {RequiredFields.simulation_time}: {self.simulation_time}
        {RequiredFields.check_polar_entering}: {self.check_polar_entering}
        ===================== project_related_fields =====================
        ================== constellation_related_fields ==================
        {RequiredFields.constellation_type}: {self.constellation_type}
        {RequiredFields.orbit_number}: {self.orbit_number}
        {RequiredFields.sat_per_orbit}: {self.sat_per_orbit}
        {RequiredFields.area_orbit_count}: {self.area_orbit_count}
        {RequiredFields.area_sat_per_orbit}: {self.area_sat_per_orbit}
        {RequiredFields.inclination}: {self.inclination}
        {RequiredFields.starting_phase}: {self.starting_phase}
        {RequiredFields.altitude}: {self.altitude}
        {RequiredFields.satellite_gsl_interface_number}: {self.satellite_gsl_interface_number}
        {RequiredFields.start_to_fail}: {self.start_to_fail}
        ================== constellation_related_fields ==================
        ================== routing protocol fields =======================
        {RequiredFields.routing_protocol}: {self.routing_protocol}
        {RequiredFields.hello_interval}: {self.hello_interval}
        {RequiredFields.router_dead_interval}: {self.router_dead_interval}
        {RequiredFields.poll_interval}: {self.poll_interval}
        {RequiredFields.retransmission_interval}: {self.retransmission_interval}
        ======================= link_related_fields ======================
        {RequiredFields.isl_link_bandwidth}: {self.isl_link_bandwidth}
        {RequiredFields.gsl_link_bandwidth}: {self.gsl_link_bandwidth}
        ======================= link_related_fields ======================
        ========================== lipsin_apps ===========================
        {RequiredFields.lipsin_apps}: {[str(item) for item in self.lipsin_apps]}
        ========================== lipsin_apps ===========================
        ======================== ground_stations =========================
        {RequiredFields.ground_stations}: {[str(item) for item in self.ground_stations]}
        ======================== ground_stations =========================
        """
        print(print_format_string)


if __name__ == "__main__":
    config_reader = ConfigReader()
    config_reader.start()
