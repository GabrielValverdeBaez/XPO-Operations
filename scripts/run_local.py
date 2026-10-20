#!/usr/bin/env python3
"""Private loopback instance; the fragment token is never logged by HTTP."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__=='__main__':
    import uvicorn
    from loadstudio.app import create_app
    app=create_app()
    print('\nXPO Load Studio - abrir esta URL en el navegador:\n')
    print('http://127.0.0.1:8765/#token='+app.state.token,flush=True)
    print('\nNo compartir la URL. Sin exposicion publica. Ctrl+C para detener.\n',flush=True)
    uvicorn.run(app,host='127.0.0.1',port=8765,access_log=False)
