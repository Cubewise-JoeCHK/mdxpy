from calendar import c
from .parser import parse_mdx
from .transformer import MDXTransformer
from mdxpy.mdx import MdxAxis, MdxBuilder, MdxTuple, Member
from TM1py.Objects.Axis import ViewAxisSelection, ViewTitleSelection
from TM1py.Objects.Subset import AnonymousSubset
from TM1py.Objects.NativeView import NativeView

def export_to_tm1py_native_view(mdx: str, view_name: str = 'mdxpy_alchemist_view'):
    assert isinstance(mdx, str), "MDX must be a string"
    assert isinstance(view_name, str), "View name must be a string"
    tree = parse_mdx(mdx)
    mdx_builder: MdxBuilder = MDXTransformer().transform(tree.children[0])
    native_view = NativeView(
        cube_name=mdx_builder.cube,
        view_name=view_name, 
        suppress_empty_columns=mdx_builder.axes.get(1, MdxAxis()).non_empty,
        suppress_empty_rows=mdx_builder.axes.get(0, MdxAxis()).non_empty,
        titles=__where_to_view_title_selection(mdx_builder),
        columns=__axis_to_view_axis(mdx_builder, 1),
        rows=__axis_to_view_axis(mdx_builder, 0),
    )
    
    return native_view
    
def __where_to_view_title_selection(mdx_builder: MdxBuilder) -> list[ViewTitleSelection]:
    if mdx_builder.where is None:
        return None
    titles = []
    for member in mdx_builder._where.members: 
        subset = AnonymousSubset(
            dimension_name=member.dimension,
            hierarchy_name=member.hierarchy,
            elements=[member.element]
        )
        title = ViewTitleSelection(
            dimension_name=member.dimension,
            subset=subset, 
            selected=member.element
        )
        titles.append(title)
    return titles 
    
def __axis_to_view_axis(mdx_builder: MdxBuilder, axis: int) -> list[ViewAxisSelection] | None:
    if mdx_builder.axes.get(axis) is None:
        return None
    axis_selection = mdx_builder.axes[axis]
    subset_list: list[ViewAxisSelection] = []
    if axis_selection.dim_sets: 
        raise NotImplementedError("Dimension sets are not supported in TM1py native views")
    if axis_selection.tuples: 
        for tuple in axis_selection.tuples:
            assert isinstance(tuple, MdxTuple), "Expected MdxTuple type"
            assert len(tuple.members) > 0, "Tuple must contain at least one member"
            assert isinstance(tuple.members[0], Member), "Tuple members must be of type Member"
            
            dimension_name = tuple.members[0].dimension
            hierarchy_name = tuple.members[0].hierarchy
            subset = AnonymousSubset(
                dimension_name=dimension_name,
                hierarchy_name=hierarchy_name,
                expression=tuple.to_mdx()
            )
            selection = ViewAxisSelection(
                dimension_name=dimension_name,
                subset=subset,
            )
            subset_list.append(selection)
    return subset_list if subset_list else None
