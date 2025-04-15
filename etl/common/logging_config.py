# logging_config.py
import os
import logging.config
import yaml


def load_logging_config(config_path: str = 'logging_config.yaml', default_level: int = logging.INFO):
    """
    Load logging configuration from YAML file.
    :param config_path: Path to configuration file
    :param default_level: Default logging level if config file not found
    :return: The loaded configuration
    """
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                return config
            except Exception as e:
                print(f"Error loading logging configuration: {e}")
                configure_basic_logging(default_level)
    else:
        configure_basic_logging(default_level)
        return None


def configure_basic_logging(level: int = logging.INFO):
    """
    Configure basic logging format as fallback.
    :param level: Logging level
    :return: None
    """

    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
