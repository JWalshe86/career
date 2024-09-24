import os
import ast
from datetime import datetime

class NaiveDatetimeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.naive_datetime_lines = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ('datetime', 'datetime.datetime'):
            if len(node.args) > 0:
                for arg in node.args:
                    # Check if the argument is a naive datetime
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, datetime) and arg.value.tzinfo is None:
                        line_number = node.lineno
                        self.naive_datetime_lines.append((line_number, arg.value))
        self.generic_visit(node)

def check_for_naive_datetimes_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as file:  # Use 'utf-8-sig' to handle BOM
            source = file.read()
        tree = ast.parse(source)
        visitor = NaiveDatetimeVisitor()
        visitor.visit(tree)
        return visitor.naive_datetime_lines
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def find_naive_datetimes_in_project(project_path):
    naive_datetime_locations = []
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                naive_datetimes = check_for_naive_datetimes_in_file(file_path)
                if naive_datetimes:
                    naive_datetime_locations.append((file_path, naive_datetimes))
    return naive_datetime_locations

if __name__ == "__main__":
    project_directory = 'path/to/your/project'  # Update with your project path
    naive_datetimes_found = find_naive_datetimes_in_project(project_directory)
    
    if naive_datetimes_found:
        print("Naive datetime instances found:")
        for file_path, locations in naive_datetimes_found:
            print(f"\nFile: {file_path}")
            for line, value in locations:
                print(f"  Line {line}: {value}")
    else:
        print("No naive datetime instances found.")

