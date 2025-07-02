
import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
import shutil
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
import chromadb

print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.load_directories(app_config=app_config)
        self.load_llm_configs(app_config=app_config)
        self.load_openai_models()



    
    def load_directories(self, app_config):
        self.sqldb_directory = str(here(app_config["directories"]["sqldb_directory"]))
        
    def load_llm_configs(self, app_config):
        self.model_name = os.getenv("deepseek/deepseek-r1-distill-llama-70b:free")

    def load_openai_models(self):
        openai_api_key = os.environ["OPENAI_API_KEY"]
        # This will be used for the GPT and embedding models
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openai_api_key ,
        )
        self.llm = ChatOpenAI(
            model_name="deepseek/deepseek-r1-distill-llama-70b:free",
            temperature=0,
            openai_api_key=openai_api_key ,
            openai_api_base="https://openrouter.ai/api/v1",
        )
    




    def remove_directory(self, directory_path: str):
        """
        Removes the specified directory.

        Parameters:
            directory_path (str): The path of the directory to be removed.

        Raises:
            OSError: If an error occurs during the directory removal process.

        Returns:
            None
        """
        if os.path.exists(directory_path):
            try:
                shutil.rmtree(directory_path)
                print(
                    f"The directory '{directory_path}' has been successfully removed.")
            except OSError as e:
                print(f"Error: {e}")
        else:
            print(f"The directory '{directory_path}' does not exist.")
