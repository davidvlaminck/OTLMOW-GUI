import PyInstaller.__main__

PyInstaller.__main__.run([
    r'Domain\mai.py',
    '--distpath', r'c:\users\[Username]]\PycharmProjects\Installers',
    '--contents-directory', 'applicationdata',
    '--paths', r'C:\Users\[Username]]\[Path to Venv]\site-packages',
    '--collect-all', 'otlmow_converter',
    '--collect-all', 'otlmow_model',
    '--collect-all', 'otlmow_template',
    '--collect-all', 'otlmow_modelbuilder',
    '--add-data', 'locale:locale',
    '--add-data', r'Domain\custom.qss:.',
    '--add-data', 'demo_projects:demo_projects',
    '--noconfirm',
    '--clean',
    '--noconsole'
])

##TODO: make sure custom.qss and demo projects are copied next to .exe > verify it is loaded same as locale
##TODO: make paths relative