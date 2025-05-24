from lark import Lark
from importlib import resources
import lark

from mdxpy.mdx import MdxBuilder
from .transformer import MDXTransformer

_PACKAGE_NAME: str = __package__ if __package__ else ""
GRAMMAR_LARK = 'grammar.lark'

assert isinstance(_PACKAGE_NAME, str), "Package name must be a string"
assert isinstance(GRAMMAR_LARK, str), "Grammar file name must be a string"

parser = Lark(resources.read_text(_PACKAGE_NAME, GRAMMAR_LARK), )

def mdx_to_tm1py_native_view(mdx: str):
    tree = parser.parse(mdx)
    mdx_builder: MdxBuilder = MDXTransformer().transform(tree.children[0])
    return mdx_builder
    