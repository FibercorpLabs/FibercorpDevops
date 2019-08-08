import os
import jinja2


class Jinja:
    
    @staticmethod
    def render(cls, tpl_path, context):
        path, filename = os.path.split(tpl_path)
        
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)
    
    @staticmethod
    def remove_empty_params(params):
        keys_to_be_removed = []
    
        for key in params:
            if params[key] is None:
                keys_to_be_removed.append(key)
    
        for key in keys_to_be_removed:
            params.pop(key)
    
        return params
