import os
import imp

import lib.models
from handlers import atlas

_models_root = os.path.dirname(lib.models.__file__)
url_definitions = []

# TODO this is bad/on;y temporary. We *should* have a file with the 
# URIs predefined. Right now we don't b/c our gcc needs to be 
# parallel. Either we need to fix our model generation process, so
# figure out a better way to load dynamically other than having a
# cache AND this
def populate_url_definitions():
    _all_uris = []
    for root, dirs, files in os.walk(_models_root):
        for f in [f for f in files if f.endswith('.py') and not f.startswith('__')]:
            m = imp.load_source('___fake', os.path.join(root, f))
            _all_uris.append(m._model_uri)
    global url_definitions
    url_definitions = [(p, atlas.AtlasHandler) for p in _all_uris]