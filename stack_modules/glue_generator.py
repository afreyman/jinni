from stack_modules.common_modules.common import Stack, StackConfig
from stack_modules.common_modules.parameters import *
from stack_modules.common_modules.helpers import NestedDict

def generator(stack=None):
    if not stack:
        print "This module requires a config file and doesn't have a default"
        exit(1)
    stack.description('Template for Glue Stack')
    glue_params = {
        "env": Parameter(
            "DeploymentEnvironment",
            Type="String",
            Default="DEV",
            Description="Environment you are building",
        )
    }

    for p in glue_params.values():
        stack.template.add_parameter(p)

    for db in stack.config['databases']:
        db_name = next(iter(db.keys()))
        stack.glue_db_adder(db_name)
        table = NestedDict(db).get(db_name + "/tables")
        for i in table.keys():
            if table[i] is None:
                table[i] = {}
            stack.glue_table_adder(i, db_name, table[i])


if __name__ == '__main__':
    stackconfig = StackConfig()
    stackconfig.loadlocalconfig("hive2athena.yml")
    mystack = Stack(stackconfig)
    mystack.description('Template for Glue Stack')
    generator(mystack)
