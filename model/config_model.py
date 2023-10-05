class ConfigModel:
    source_code_path = ''
    script_code_path = ''
    flavors = ''
    environments = ''

    def toConfigModel(self, json):
        self.source_code_path = json['sourceCodePath']
        self.script_code_path = json['scriptCodePath']
        self.flavors = json['flavors']
        self.environments = json['environments']
