class Strategy:
    name: str
    desc: str = ""

    def run(self, **args):
        print(f"\nRunning {self.name} strategy [{self.desc}]\n")