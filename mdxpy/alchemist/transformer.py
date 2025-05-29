from mdxpy.mdx import *
import lark

class MDXTransformer(lark.Transformer):
    def child(self, item):
        return item[0].value
    
    def consolidation(self, item): 
        return None
    
    def name(self, item):
        # syntax : [ IDENTIFIER ] 
        return [i for i in item if isinstance(i, str)][1]
    
    def dimension(self, item):
        return ('dimension', item[0])

    def hierarchy(self, item):
        return ('hierarchy', item[0])

    def element(self, item):
        return ('element', item[0])
    
    def member(self, item): 
        data = {i[0]: i[1] for i in item if isinstance(i, tuple)}
        try:
            return Member(
                dimension=data['dimension'],
                hierarchy=data.get('hierarchy', data['dimension']),
                element=data['element']
            )
        except Exception as e:
            breakpoint()
    
    def mdx_tuple(self, item):
        return MdxTuple(
            members=[i for i in item if isinstance(i, Member)]
        )
        
    def mdx_axis_row(self, item):
        mdx_axis = MdxAxis.empty()
        for node in item: 
            if isinstance(node, lark.Token): 
                continue 
            if isinstance(node, MdxTuple):
                mdx_axis.add_tuple(node)
        return ('row', mdx_axis)
    
    def where(self, item): 
        return ('where', [i for i in item if isinstance(i, MdxTuple)][0])
    
    def cube_source(self, item):
        return ('cube', item[0])
    
    def mdx_axis_column(self, item):
        mdx_axis = MdxAxis.empty()
        for node in item: 
            if isinstance(node, lark.Token): 
                continue 
            if isinstance(node, MdxTuple):
                mdx_axis.add_tuple(node)
        return ('column', mdx_axis)

    def mdx_builder(self, item):
        
        data = {i[0]: i[1] for i in item if isinstance(i, tuple)}
        builder = MdxBuilder(
            cube = data['cube'],
        )
        axes = {}
        if row_data := data.get('row'):
            axes.update({0: row_data})
        if column_data := data.get('column'):
            axes.update({1: column_data})
        builder.axes = axes
        builder._where = where if (where := data.get('where')) else MdxTuple.empty()
        return builder
        
    def mdx_hierarchy_set(self, item):
        return item

    def tuples_set(self, item): 
        return TuplesSet(item)      
