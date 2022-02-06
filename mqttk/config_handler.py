import sys
import os
from pathlib import Path
import json


LOAD = "load"
SAVE = "save"


class ConfigHandler:
    def __init__(self):
        """
        Config handler.

        configuration_dict = {
            "connections": {}
            "last_used_connection": connection name,
            "window_geometry: last used window geometry string,
            "autoscroll: true/false
        }

        configuration_dict[connections] = {
            "connection_profile_name": {
                "connection_parameters": {
                    "connection_parameter: value
                },
                "subscriptions": [] list of previous subscriptions
                "publish_topics": [] list of previous publishes
                "stored_publishes": {
                    "name": {
                        "topic": topic,
                        "qos": qos,
                        "payload": payload,
                        "retained": retained
                },
                "last_publish_used": last publish,
                "last_subscribe_used: last subscribe
            }
        }

        connection parameters:
        - broker_addr
        - broker_port
        - client_id
        - user
        - pass
        - timeout
        - keepalive
        - mqtt_version
        - ssl
        - ca_file
        - cl_cert
        - cl_key

        """
        self.configuration_dict = {}
        self.wont_save = False
        self.config_file_manager(LOAD)
        self.first_start = True

    def config_file_manager(self, action):
        if sys.platform.startswith("win"):
            appdata_dir = os.getenv('LOCALAPPDATA')
            config_dir = os.path.join(appdata_dir, "MQTTk")
            config_file = os.path.join(appdata_dir, "MQTTk", "MQTTk-config.json")

        elif sys.platform.startswith("linux"):
            self.configuration_dict = {}
            home_dir = str(Path.home())
            config_dir = os.path.join(home_dir, ".config", "MQTTk")
            config_file = os.path.join(home_dir, ".config", "MQTTk", "MQTTk-config.json")

        elif sys.platform.startswith("darwin"):
            home_dir = str(Path.home())
            config_dir = os.path.join(home_dir, "Library", "ApplicationSupport", "MQTTk")
            config_file = os.path.join(home_dir, "Library", "ApplicationSupport", "MQTTk", "MQTTk-config.json")
        else:
            self.wont_save = True
            raise AssertionError

        if not os.path.isfile(config_file):
            self.first_start = True
            if not os.path.isdir(config_dir):
                os.makedirs(config_dir)
            with open(config_file, "w") as configfile:
                configfile.write("{}")

        else:
            if action == LOAD:
                with open(config_file, "r") as configfile:
                    configuration = configfile.read()
                try:
                    self.configuration_dict = json.loads(configuration)
                except Exception as e:
                    print("Failed to load config", e)
            else:
                with open(config_file, "w") as config_file:
                    try:
                        config_string = json.dumps(self.configuration_dict, indent=2)
                    except Exception as e:
                        print("Failed to save configuration", e)
                    else:
                        config_file.write(config_string)

    def get_connection_profiles(self):
        return list(self.configuration_dict.get("connections", {}).keys())

    def get_connection_config_dict(self, connection):
        return self.configuration_dict.get("connections", {}).get(connection, {})

    def remove_connection_config(self, connection_name):
        self.configuration_dict.get("connections", {}).pop(connection_name, None)
        self.config_file_manager(SAVE)

    def save_connection_config(self, connection_name, connection_config):
        if "connections" not in self.configuration_dict:
            self.configuration_dict["connections"] = {}
        if connection_name not in self.configuration_dict["connections"]:
            self.configuration_dict["connections"][connection_name] = {
                "connection_parameters": {},
                "subscriptions": [],
                "publish_topics": [],
                "stored_publishes": {}
            }
            self.configuration_dict["connections"][connection_name]["connection_parameters"] = connection_config
        self.config_file_manager(SAVE)

    def add_subscription_history(self, connection, topic):
        if topic not in self.configuration_dict["connections"][connection]["subscriptions"]:
            self.configuration_dict["connections"][connection]["subscriptions"].append(topic)
        self.configuration_dict["connections"][connection]["last_subscribe_used"] = topic
        self.config_file_manager(SAVE)

    def get_window_geometry(self):
        return self.configuration_dict.get("window_geometry", None)

    def save_window_geometry(self, window_geometry):
        self.configuration_dict["window_geometry"] = window_geometry
        self.config_file_manager(SAVE)

    def get_last_used_connection(self):
        return self.configuration_dict.get("last_used_connection", "")

    def update_last_used_connection(self, connection):
        self.configuration_dict["last_used_connection"] = connection

    def get_autoscroll(self):
        return bool(self.configuration_dict.get("autoscroll", False))

    def save_autoscroll(self, value):
        self.configuration_dict["autoscroll"] = value
        self.config_file_manager(SAVE)

    def delete_publish_history_item(self, connection, name):
        try:
            self.configuration_dict["connections"][connection]["stored_publishes"].pop(name, None)
        except Exception as e:
            print("Failed to remove history publish item", e, connection, name)

    def get_publish_history(self, connection):
        return self.configuration_dict["connections"].get(connection, {}).get("stored_publishes", {})

    def save_publish_history_item(self, connection, name, config):
        try:
            if "stored_publishes" not in self.configuration_dict["connections"][connection]:
                self.configuration_dict["connections"][connection]["stored_publishes"] = {
                    name: config
                }
            else:
                self.configuration_dict["connections"][connection]["stored_publishes"][name] = config
            self.config_file_manager(SAVE)
        except Exception as e:
            print("Exception saving publish history config", e)

    def get_publish_topic_history(self, connection):
        return self.configuration_dict["connections"].get(connection, {}).get("publish_topics", [])

    def save_publish_topic_history_item(self, connection, topic):
        try:
            new = True
            if "publish_topics" not in self.configuration_dict["connections"][connection]:
                self.configuration_dict["connections"][connection]["publish_topics"] = [topic]
            else:
                if topic not in self.configuration_dict["connections"][connection]["publish_topics"]:
                    self.configuration_dict["connections"][connection]["publish_topics"].append(topic)
                else:
                    new = False
            self.configuration_dict["connections"][connection]["last_publish_used"] = topic
            self.config_file_manager(SAVE)
            return new
        except Exception as e:
            print("Error saving publish topic history item", e)
        self.config_file_manager(SAVE)

    def get_last_publish_topic(self, connection):
        return self.configuration_dict.get("connections", {}).get(connection, {}).get("last_publish_used", "")

    def get_last_subscribe_used(self, connection):
        return self.configuration_dict.get("connections", {}).get(connection, {}).get("last_subscribe_used", "")
