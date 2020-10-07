
def create_c_setup(mod_name, dependencies, compiler, flags):
    code  = "from setuptools import Extension, setup\n\n"

    flags = flags.replace('"','\\"')
    deps  = ", ".join("r\"{0}.c\"".format(d) for d in dependencies)
    code += "extension_mod = Extension(\"{0}\", [{1}], extra_compile_args = {2})\n\n".format(mod_name, deps, flags.strip().split())
    code += "setup(name = \"" + mod_name + "\", ext_modules=[extension_mod])"
    return code
