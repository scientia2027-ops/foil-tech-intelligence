#!/usr/bin/env python3
"""Keep file:// and ZIP preview working by embedding JSON fallback in index.html."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parents[1]
html=root/'index.html'
raw=html.read_text('utf8')
data=json.loads((root/'data/issues.json').read_text('utf8'))
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
new,n=re.subn(r'(<script type="application/json" id="embedded-data">).*?(</script>)',lambda m:m.group(1)+payload+m.group(2),raw,flags=re.S)
if n!=1:raise RuntimeError('could not find embedded data tag')
html.write_text(new,'utf8')
print('Embedded',len(data['editions']),'issues')
