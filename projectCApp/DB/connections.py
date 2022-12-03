from sqlalchemy import create_engine
import json

class Engine():
    def __init__(self,configPath="D:\pythonProjectC\config\sqlConfig.json"):
        with open(configPath,"r") as file:
            config = json.load(file)
            self.user = config["user"]
            self.pwd = config["pwd"]
            self.host = config["host"]
            self.database = config["database"]
            self.url = f"mysql+pymysql://{self.user}:{self.pwd}@{self.host}/{self.database}"
            self.engine = create_engine(self.url,echo=True)

    def getConnection(self):
        return self.engine

