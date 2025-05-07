from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
import builtins
import ast
import re

def execute_user_code(user_code, user_func, *args, **kwargs):
    """ Executed user code in restricted env
        Args:
            user_code(str) - String containing the unsafe code
            user_func(str) - Function inside user_code to execute and return value
            *args, **kwargs - arguments passed to the user function
        Return:
            Return value of the user_func
    """
    _SAFE_MODULES = frozenset((
        "math",
        "collections",
        "itertools",
        ))

    def _safe_import(name, *args, **kwargs):
        if name not in _SAFE_MODULES:
            raise Exception(f"{name!r} is not a supported import")
        return __import__(name, *args, **kwargs)

    def _inplacevar_(op, var, expr):
        if op == "+=":
            return var + expr
        elif op == "-=":
            return var - expr
        elif op == "*=":
            return var * expr
        elif op == "/=":
            return var / expr
        elif op == "%=":
            return var % expr
        elif op == "**=":
            return var ** expr
        elif op == "<<=":
            return var << expr
        elif op == ">>=":
            return var >> expr
        elif op == "|=":
            return var | expr
        elif op == "^=":
            return var ^ expr
        elif op == "&=":
            return var & expr
        elif op == "//=":
            return var // expr
        elif op == "@=":
            return var // expr

    def _apply(f, *a, **kw):
        return f(*a, **kw)

    try:
        restricted_locals = {
            "result": None,
            "args": args,
            "kwargs": kwargs,
        }

        restricted_globals = {
            "__builtins__": {
                **safe_builtins,    
                "__import__": _safe_import,
                "dict": getattr(builtins, "dict"),
                "list": getattr(builtins, "list"),
                "map": getattr(builtins, "map"),
                "set": getattr(builtins, "set"),
                "sum": getattr(builtins, "sum"),
                "type": getattr(builtins, 'type'),
            },
            '_inplacevar_':  _inplacevar_,
            "_getitem_": default_guarded_getitem,
            "_apply_": _apply,
            "_getiter_": default_guarded_getiter,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence
        }

        # Add another line to user code that executes @user_func
        user_code += "\nresult = {0}(*args, **kwargs)".format(user_func)

        # Compile the user code
        byte_code = compile_restricted(user_code, filename="<user_code>", mode="exec")

        # Run it
        exec(byte_code, restricted_globals, restricted_locals)

        # User code has modified result inside restricted_locals. Return it.
        return restricted_locals["result"]
    except Exception as e:
        raise e

def testCode(stringCode, stringTest):
    try:
        stringTest = stringTest.replace("[", "(").replace("]", ",),")
        testingDict = ast.literal_eval(stringTest)
    except Exception as e:
        return f"Unable to Create Testing. {e}"
    
    if type(testingDict) != type(dict()):
        return "Unable to Create Testing."
    
    funcName = re.search(r'def (.*?)\(', stringCode).group(1)
    if funcName == None:
        return "Unable to Resolve Function Name."
    
    for test in testingDict:
        try:
            result = execute_user_code(stringCode, funcName, *test)
        except Exception as e:
            return f"An Error has Occured in the Code Block. {e}"

        if result != testingDict[test]:
            return f"Test input {test} failed, to match output {testingDict[test]}"
        
    return "All tests passed."
    
