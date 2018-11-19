# -*- coding: utf-8 -*-

from collections import OrderedDict
import redbaron
import traceback
import importlib
import pickle
import os
import sys
import re

#==============================================================================

from redbaron import RedBaron
from redbaron import StringNode, IntNode, FloatNode, ComplexNode
from redbaron import FloatExponantNode, StarNode
from redbaron import NameNode
from redbaron import AssignmentNode
from redbaron import CommentNode, EndlNode
from redbaron import ComparisonNode
from redbaron import ComparisonOperatorNode
from redbaron import UnitaryOperatorNode
from redbaron import BinaryOperatorNode, BooleanOperatorNode
from redbaron import AssociativeParenthesisNode
from redbaron import DefNode
from redbaron import ClassNode
from redbaron import TupleNode, ListNode
from redbaron import CommaProxyList
from redbaron import LineProxyList
from redbaron import ListComprehensionNode
from redbaron import ComprehensionLoopNode
from redbaron import ArgumentGeneratorComprehensionNode
from redbaron import NodeList
from redbaron import DotProxyList
from redbaron import ReturnNode
from redbaron import PassNode
from redbaron import DefArgumentNode
from redbaron import ForNode
from redbaron import PrintNode
from redbaron import DelNode
from redbaron import DictNode, DictitemNode
from redbaron import WhileNode
from redbaron import IfelseblockNode, IfNode, ElseNode, ElifNode
from redbaron import TernaryOperatorNode
from redbaron import DotNode
from redbaron import CallNode
from redbaron import CallArgumentNode
from redbaron import AssertNode
from redbaron import ExceptNode
from redbaron import FinallyNode
from redbaron import RaiseNode
from redbaron import TryNode
from redbaron import YieldNode
from redbaron import YieldAtomNode
from redbaron import BreakNode, ContinueNode
from redbaron import GetitemNode, SliceNode
from redbaron import ImportNode, FromImportNode
from redbaron import DottedAsNameNode, DecoratorNode
from redbaron import NameAsNameNode
from redbaron import LambdaNode
from redbaron import WithNode
from redbaron import AtomtrailersNode

#==============================================================================

from pyccel.ast import NativeInteger, NativeReal
from pyccel.ast import NativeBool, NativeComplex
from pyccel.ast import NativeRange
from pyccel.ast import NativeIntegerList
from pyccel.ast import NativeRealList
from pyccel.ast import NativeComplexList
from pyccel.ast import NativeList
from pyccel.ast import NativeSymbol
from pyccel.ast import String
from pyccel.ast import DataTypeFactory
from pyccel.ast import Nil, Void
from pyccel.ast import Variable
from pyccel.ast import DottedName, DottedVariable
from pyccel.ast import Assign, AliasAssign, SymbolicAssign
from pyccel.ast import AugAssign, CodeBlock
from pyccel.ast import Return
from pyccel.ast import Pass
from pyccel.ast import ConstructorCall
from pyccel.ast import FunctionDef, Interface
from pyccel.ast import PythonFunction, SympyFunction
from pyccel.ast import ClassDef
from pyccel.ast import GetDefaultFunctionArg
from pyccel.ast import For, FunctionalFor, ForIterator
from pyccel.ast import GeneratorComprehension as GC
from pyccel.ast import FunctionalSum, FunctionalMax, FunctionalMin
from pyccel.ast import If, IfTernaryOperator
from pyccel.ast import While
from pyccel.ast import Print
from pyccel.ast import SymbolicPrint
from pyccel.ast import Del
from pyccel.ast import Assert
from pyccel.ast import Comment, EmptyLine, NewLine
from pyccel.ast import Break, Continue
from pyccel.ast import Slice, IndexedVariable, IndexedElement
from pyccel.ast import FunctionHeader, ClassHeader, MethodHeader
from pyccel.ast import VariableHeader, InterfaceHeader
from pyccel.ast import MetaVariable
from pyccel.ast import MacroFunction, MacroVariable
from pyccel.ast import Concatinate
from pyccel.ast import ValuedVariable
from pyccel.ast import Argument, ValuedArgument
from pyccel.ast import Is
from pyccel.ast import Import, TupleImport
from pyccel.ast import AsName
from pyccel.ast import AnnotatedComment, CommentBlock
from pyccel.ast import With, Block
from pyccel.ast import Range, Zip, Enumerate, Product, Map
from pyccel.ast import List, Dlist, Len
from pyccel.ast import builtin_function as pyccel_builtin_function
from pyccel.ast import builtin_import as pyccel_builtin_import
from pyccel.ast import builtin_import_registery as pyccel_builtin_import_registery
from pyccel.ast import Macro
from pyccel.ast import MacroShape
from pyccel.ast import construct_macro
from pyccel.ast import SumFunction, Subroutine
from pyccel.ast import Zeros, Where, Linspace, Diag, Complex
from pyccel.ast import inline, subs, create_variable, extract_subexpressions

from pyccel.ast.core      import local_sympify, int2float, Pow, _atomic
from pyccel.ast.datatypes import sp_dtype, str_dtype


from pyccel.parser.utilities import omp_statement, acc_statement
from pyccel.parser.utilities import fst_move_directives
from pyccel.parser.utilities import reconstruct_pragma_multilines
from pyccel.parser.utilities import is_valid_filename_pyh, is_valid_filename_py
from pyccel.parser.utilities import read_file
from pyccel.parser.utilities import get_default_path

from pyccel.parser.syntax.headers import parse as hdr_parse
from pyccel.parser.syntax.openmp  import parse as omp_parse
from pyccel.parser.syntax.openacc import parse as acc_parse

from pyccel.parser.errors import Errors, PyccelSyntaxError
from pyccel.parser.errors import PyccelSemanticError

# TODO - remove import * and only import what we need
#      - use OrderedDict whenever it is possible

from pyccel.parser.messages import *

#==============================================================================

from sympy.core.function       import Function, FunctionClass, Application
from sympy.core.numbers        import ImaginaryUnit
from sympy.logic.boolalg       import Boolean, BooleanTrue, BooleanFalse
from sympy.utilities.iterables import iterable as sympy_iterable
from sympy.core.assumptions    import StdFactKB

from sympy import Sum as Summation
from sympy import KroneckerDelta, Heaviside
from sympy import Symbol, sympify, symbols
from sympy import Eq, Ne, Lt, Le, Gt, Ge
from sympy import NumberSymbol, Number
from sympy import Indexed, IndexedBase
from sympy import Add, Mul, And, Or
from sympy import FunctionClass
from sympy import ceiling, floor, Mod
from sympy import Min, Max

from sympy import oo  as INF
from sympy import Pow as sp_Pow
from sympy import Integer, Float
from sympy import true, false
from sympy import Tuple
from sympy import Lambda
from sympy import Atom
from sympy import Expr
from sympy import Dict
from sympy import Not
from sympy import cache

errors = Errors()
#==============================================================================

strip_ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|[\n\t\r]')

redbaron.ipython_behavior = False

# use this to delete ansi_escape characters from a string
# Useful for very coarse version differentiation.

#==============================================================================

def is_ignored_module(name):
    if isinstance(name, DottedName):
        if str(name) in ['pyccel.decorators']:
            return True

    return False


def get_filename_from_import(module,output_folder='',context_import_path = {}):
    """Returns a valid filename with absolute path, that corresponds to the
    definition of module.
    The priority order is:
        - header files (extension == pyh)
        - python files (extension == py)
    """

    filename_pyh = '{}.pyh'.format(module.replace('.','/'))
    filename_py = '{}.py'.format(module.replace('.','/'))

    if is_valid_filename_pyh(filename_pyh):
        return os.path.abspath(filename_pyh)
    if is_valid_filename_py(filename_py):
        return os.path.abspath(filename_py)

    if (module in context_import_path):
        poss_filename_pyh = '{0}{1}.pyh'.format(context_import_path[module],module)
        poss_filename_py = '{0}{1}.py'.format(context_import_path[module],module)
        if is_valid_filename_pyh(poss_filename_pyh):
            return os.path.abspath(poss_filename_pyh)
        if is_valid_filename_py(poss_filename_py):
            return os.path.abspath(poss_filename_py)

    folders = output_folder.split(""".""")
    for i in range(len(folders)):
        poss_dirname      = os.path.join( *folders[:i+1] )
        poss_filename_pyh = os.path.join( poss_dirname, filename_pyh )
        poss_filename_py  = os.path.join( poss_dirname, filename_py  )
        if is_valid_filename_pyh(poss_filename_pyh):
            return os.path.abspath(poss_filename_pyh)
        if is_valid_filename_py(poss_filename_py):
            return os.path.abspath(poss_filename_py)

    source = module
    if len(module.split(""".""")) > 1:

        # we remove the last entry, since it can be a pyh file

        source = """.""".join(i for i in module.split(""".""")[:-1])
        _module = module.split(""".""")[-1]
        filename_pyh = '{}.pyh'.format(_module)
        filename_py = '{}.py'.format(_module)

    try:
        package = importlib.import_module(source)
        package_dir = str(package.__path__[0])
    except:
        errors = Errors()
        errors.report(PYCCEL_UNFOUND_IMPORTED_MODULE, symbol=source,
                      severity='fatal')

    filename_pyh = os.path.join(package_dir, filename_pyh)
    filename_py = os.path.join(package_dir, filename_py)
    if os.path.isfile(filename_pyh):
        return filename_pyh
    elif os.path.isfile(filename_py):
        return filename_py

    errors = Errors()
    errors.report(PYCCEL_UNFOUND_IMPORTED_MODULE, symbol=module,
                  severity='fatal')


#==============================================================================

class BasicParser(object):

    """ Class for a base Parser."""

    def __init__(self,
                 debug=False,
                 headers=None,
                 static=None,
                 show_traceback=True,
                 output_folder='',
                 context_import_path = {}):
        """Parser constructor.

        debug: bool
            True if in debug mode.

        headers: list, tuple
            list of headers to append to the namespace

        static: list/tuple
            a list of 'static' functions as strings

        show_traceback: bool
            prints Tracebacke exception if True

        """
        self._fst = None
        self._ast = None

        self._filename  = None
        self._metavars  = {}
        self._namespace = {}

        self._namespace['imports'       ] = OrderedDict()
        self._namespace['variables'     ] = {}
        self._namespace['classes'       ] = {}
        self._namespace['functions'     ] = {}
        self._namespace['macros'        ] = {}
        self._namespace['cls_constructs'] = {}

        self._namespace['symbolic_functions']   = {}
        self._namespace['python_functions'  ]   = {}
        self._scope = {}

        self._output_folder       = output_folder
        self._context_import_path = context_import_path

        # represent the namespace of a function

        self._current_class = None
        self._current       = None

        # we use it to detect the current method or function
        self._imports = {}

        # the following flags give us a status on the parsing stage
        self._syntax_done   = False
        self._semantic_done = False

        # current position for errors

        self._bounding_box = None

        # flag for blocking errors. if True, an error with this flag will cause
        # Pyccel to stop
        # TODO ERROR must be passed to the Parser __init__ as argument

        self._blocking = False

        # printing exception

        self._show_traceback = show_traceback

        # TODO use another name for headers
        #      => reserved keyword, or use __

        self._namespace['headers'] = {}
        if headers:
            if not isinstance(headers, dict):
                raise TypeError('Expecting a dict of headers')

            for (key, value) in list(headers.items()):
                self._namespace['headers'][key] = value

        self._namespace['static'] = []
        if static:
            if not isinstance(static, (list, tuple)):
                raise TypeError('Expecting a list/tuple of static')

            for i in static:
                if not isinstance(i, str):
                    raise TypeError('Expecting str. given {}'.format(type(i)))

            self._namespace['static'] = static

    @property
    def namespace(self):
        return self._namespace

    @property
    def headers(self):
        return self.namespace['headers']

    @property
    def imports(self):
        return self.namespace['imports']

    @property
    def functions(self):
        return self.namespace['functions']

    @property
    def variables(self):
        return self.namespace['variables']

    @property
    def classes(self):
        return self.namespace['classes']

    @property
    def python_functions(self):
        return self.namespace['python_functions']

    @property
    def symbolic_functions(self):
        return self.namespace['symbolic_functions']

    @property
    def static_functions(self):
        return self.namespace['static']

    @property
    def macros(self):
        return self.namespace['macros']

    @property
    def filename(self):
        return self._filename

    @property
    def code(self):
        return self._code

    @property
    def fst(self):
        return self._fst

    @property
    def ast(self):
        if self._ast is None:
            self._ast = self.parse()
        return self._ast

    @property
    def metavars(self):
        return self._metavars

    @property
    def current_class(self):
        return self._current_class

    @property
    def syntax_done(self):
        return self._syntax_done

    @property
    def semantic_done(self):
        return self._semantic_done

    @property
    def is_header_file(self):
        """Returns True if we are treating a header file."""

        if self.filename:
            return self.filename.split(""".""")[-1] == 'pyh'
        else:
            return False

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def blocking(self):
        return self._blocking

    @property
    def show_traceback(self):
        return self._show_traceback

    # TODO shall we need to export the Parser too?

    def dump(self, filename=None):
        """Dump the current ast using Pickle.

        filename: str
            output file name. if not given `name.pyccel` will be used and placed
            in the Pyccel directory ($HOME/.pyccel)
        """

        # ...

        use_home_dir = False
        if not filename:
            if not self.filename:
                raise ValueError('Expecting a filename to load the ast')

            use_home_dir = True
            name = os.path.basename(self.filename)
            filename = '{}.pyccel'.format(name)

        # check extension

        if not filename.split(""".""")[-1] == 'pyccel':
            raise ValueError('Expecting a .pyccel extension')

#        print('>>> home = ', os.environ['HOME'])
        # ...

        # we are only exporting the AST.

        f = open(filename, 'wb')
        pickle.dump(self.ast, f, protocol=2)
        f.close()
        print ('> exported :', self.ast)

    # TODO shall we need to load the Parser too?

    def load(self, filename=None):
        """Load the current ast using Pickle.

        filename: str
            output file name. if not given `name.pyccel` will be used and placed
            in the Pyccel directory ($HOME/.pyccel)
        """

        # ...

        use_home_dir = False
        if not filename:
            if not self.filename:
                raise ValueError('Expecting a filename to load the ast')

            use_home_dir = True
            name = os.path.basename(self.filename)
            filename = '{}.pyccel'.format(name)

        # check extension

        if not filename.split(""".""")[-1] == 'pyccel':
            raise ValueError('Expecting a .pyccel extension')

#        print('>>> home = ', os.environ['HOME'])
        # ...

        f = open(filename, 'rb')
        self._ast = pickle.load(f)
        f.close()
        print ('> loaded   :', self.ast)

    def insert_function(self, func):
        """."""

        if isinstance(func, SympyFunction):
            self.insert_symbolic_function(func)
        elif isinstance(func, PythonFunction):
            self.insert_python_function(func)
        elif isinstance(func, (FunctionDef, Interface)):
            container = self._namespace['functions']
            if isinstance(self._current, DottedName):
                name = self._current.name[0]
                container = self._scope[name]['functions']
            container[str(func.name)] = func
        else:
            raise TypeError('Expected a Function definition')

    def insert_symbolic_function(self, func):
        """."""

        container = self._namespace['symbolic_functions']
        if isinstance(self._current, DottedName):
            name = self._current.name[0]
            container = self._scope[name]['symbolic_functions']
        if isinstance(func, SympyFunction):
            container[str(func.name)] = func
        elif isinstance(func, SymbolicAssign) and isinstance(func.rhs,
                Lambda):
            container[str(func.lhs)] = func.rhs
        else:
            raise TypeError('Expected a symbolic_function')

    def insert_python_function(self, func):
        """."""

        container = self._namespace['python_functions']
        if isinstance(self._current, DottedName):
            name = self._current.name[0]
            container = self._scope[name]['python_functions']

        if isinstance(func, PythonFunction):
            container[str(func.name)] = func
        else:
            raise TypeError('Expected a python_function')

    def insert_import(self, expr):
        """."""

        # TODO improve

        if not isinstance(expr, Import):
            raise TypeError('Expecting Import expression')
        container = self._namespace['imports']
        if self._current:
            self._scope[self._current]['imports'].append(expr)

        # if source is not specified, imported things are treated as sources
        # TODO test if builtin import

        source = expr.source
        if source is None:
            for t in expr.target:
                name = str(t)
                container[name] = None
        else:
            source = str(source)
            if not source in pyccel_builtin_import_registery:
                for t in expr.target:
                    name = [str(t)]
                    if not source in container.keys():
                        container[source] = []
                    container[source] += name

    def print_namespace(self):

        # TODO improve spacing

        print ('------- namespace -------')
        for (k, v) in self.namespace.items():
            print ('{var} \t :: \t {dtype}'.format(var=k, dtype=type(v)))
        print ('-------------------------')

    def view_namespace(self, entry):

        # TODO improve

        try:
            from tabulate import tabulate

            table = []
            for (k, v) in self.namespace[entry].items():
                k_str = '{}'.format(k)
                if entry == 'imports':
                    if v is None:
                        v_str = '*'
                    else:
                        v_str = '{}'.format(v)
                elif entry == 'variables':
                    v_str = '{}'.format(type(v))
                else:
                    raise NotImplementedError('TODO')

                line = [k_str, v_str]
                table.append(line)
            headers = ['module', 'target']

#            txt = tabulate(table, headers, tablefmt="rst")

            txt = tabulate(table, tablefmt='rst')
            print (txt)
        except:

            print ('------- namespace.{} -------'.format(entry))
            for (k, v) in self.namespace[entry].items():
                print ('{var} \t :: \t {value}'.format(var=k, value=v))
            print ('-------------------------')

    def _visit(self, expr, **settings):
        raise NotImplementedError('Must be implemented by the extension')

#==============================================================================


if __name__ == '__main__':
    import sys

    try:
        filename = sys.argv[1]
    except:
        raise ValueError('Expecting an argument for filename')

    parser = BasicParser(filename)
