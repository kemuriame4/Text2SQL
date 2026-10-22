from omegaconf import OmegaConf


def load_config(config_path: str):
    config = OmegaConf.load(str(config_path))
    schema = OmegaConf.structured(config)
    config = OmegaConf.to_object(OmegaConf.merge(config, schema))
    return  config