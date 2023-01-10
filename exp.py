# Python syntax experiments during development

import json
import pprint
json_file = open("config-ailab1.jsn")
json_data = json_file.read()
data_dict = json.loads(json_data)

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data_dict)

json_file.close()


