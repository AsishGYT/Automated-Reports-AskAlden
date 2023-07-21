import os
def load_env_vars(py_file):
    # Retrieve all variables from py_file
    variables = [var for var in dir(py_file) if not var.startswith('__')]

    # Load the variables into the env
    for var_name in variables:
        var_value = getattr(py_file, var_name)
        os.environ[var_name] = var_value
