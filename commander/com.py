from typing import Callable
from datetime import datetime
import inspect

class Commander:
    def __init__(self, logs=True):
        self.tree = {}
        self.logs=logs
    
    def show_tree(self, node=None, depth=0):
        if node is None:
            node = self.tree

        result = ""

        for key in node:
            if key != 'func':
                result += "  " * depth + f'{depth+1} {key}' + "\n"
                result += self.show_tree(node[key], depth + 1)
            else:
                argspec = inspect.getfullargspec(node[key])
                argument_names = argspec.args
                args_str = ", ".join(map(str, argument_names))
                result += "  " * depth + f"-- {args_str}\n"

        return result

    def add_command(self, command: list[str], func: Callable):
        current_level = self.tree
        for part in command:
            if part not in current_level:
                current_level[part.lower()] = {}
            current_level = current_level[part]
        current_level['func'] = func

    def decode_str(self, prompt: str):
        elements = prompt.split(' ')
        command = []
        params = []
        for el in elements:
            if '--' in el:
                params.append(el.split('--')[-1])
            else:
                command.append(el)
        return command, params


    async def exec_command(self, prompt: str):
        command, params = self.decode_str(prompt.lower())
        current_level = self.tree
        for part in command:
            if part in current_level:
                current_level = current_level[part]
            else:
                if self.logs:
                    print(f"{datetime.now()} Command not found: {' '.join(command)}")
                return

        func = current_level.get('func')
        if func:
            await func(*params)
            if self.logs:
                print(f"{datetime.now()} Command successfuly executed: {' '.join(command)}")
        else:
            if self.logs:
                print(f"{datetime.now()} No function assigned for command: {' '.join(command)}")

        

