import json
from troposphere import Ref

# little helper function to convert strings to json and return Novalue Ref

def dictConvert(string):
    try:
        converted_str = json.loads(string)
        return converted_str
    except Exception as e:
        converted_str = Ref("AWS::NoValue")
        return converted_str

# little helper class to search nested dicts.
class NestedDict(dict):
    ''' little helper to find stuff '''
    def get(self, path, default=None):
        keys = path.split("/")
        val = None
        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)
            if not val:
                break
        return val