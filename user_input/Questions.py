from user_input import Validator

PROJECT_QUESTION = [
    {
        "type": "input",
        "name": "project_name",
        "message": "What is the name of your project?",
        "default": "constellation"
    }
]

LINK_QUESTION = [
    {
        "type": "list",
        "name": "bandwidth",
        "message": "What is the bandwidth of your inter satellite link?",
        "choices": [
            "10 Mbps",
            "100 Mbps",
            "1000 Mbps"
        ]
    }
]

ROUTING_PROTOCOL_QUESTION = [
    {
        "type": "list",
        "name": "protocol",
        "message": "what is the routing protocol on your satellite?",
        "choices": [
            "IP_OSPF",
            "LIPSIN",
        ]
    }
]

CONSTELLATION_QUESTION = [
    {
        "type": "list",
        "name": "constellation_type",
        "message": "What is the type of your constellation?",
        "choices": [
            "Walker_Star",
            "Walker_Delta",
        ]
    },
    {
        "type": "input",
        "name": "orbit_number",
        "message": "How many orbits do you want?",
        "default": "6",
        "validate": Validator.IntegerValidator
    },
    {
        "type": "input",
        "name": "sat_per_orbit",
        "message": "How many satellites do you want per orbit?",
        "default": "11",
        "validate": Validator.IntegerValidator
    },
    {
        "type": "input",
        "name": "inclination",
        "message": "What is the inclination of your constellation?",
        "default": "90",
        "validate": Validator.FloatValidator
    },
    {
        "type": "input",
        "name": "starting_phase",
        "message": "What is the starting phase of your constellation?",
        "default": "0",
        "validate": Validator.FloatValidator
    },
    {
        "type": "input",
        "name": "altitude",
        "message": "What is the altitude of your constellation? (km)",
        "default": "550",
        "validate": Validator.FloatValidator
    }
]

IF_ADD_LIPSIN_APP_QUESTION = [
    {
        "type": "list",
        "name": "add_or_not",
        "message": "Do you want to add an application?",
        "choices": [
            "Yes",
            "No"
        ]
    }
]

LIPSIN_APP_QUESTION = [
    {
        "type": "input",
        "name": "source",
        "message": "What is the source satellite id?",
        "default": "1",
    },
    {
        "type": "input",
        "name": "destinations",
        "message": "What is the destination satellite id? (please separate these ids by , like 9,10,12)",
        "default": "2",
    },
    {
        "type": "list",
        "name": "continue",
        "message": "Do you want to add more destination satellites?",
        "choices": [
            "Yes",
            "No"
        ]
    }
]

LINK_CAPACITY_SETTING_QUESTION = [
    {
        "type": "input",
        "name": "packet_capacity",
        "message": "what is the packet capacity of the ethernet interface",
        "default": "500",
        "validate": Validator.IntegerValidator
    }
]
