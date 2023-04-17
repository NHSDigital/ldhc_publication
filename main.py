from pipeline import pipeline_wrapper
from pipeline.utils.config import load_config

def main() -> None:
    """
    Runs the pipeline in production or test mode
    """
    config_file = load_config.load_config("config.json")
    pipeline_wrapper.run(config_file)


if __name__=="__main__":
    main()