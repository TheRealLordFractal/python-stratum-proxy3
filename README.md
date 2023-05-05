# python-stratum-proxy3
Stratum mining proxy for SHA256 coins written in python 3.17

This mining proxy is written in python 3.1x and allows proxying for SHA256 crypto currency pools.

Initial Release 1.0 -

To get running install the pyyaml python lib via pip


-make sure to edit config.yml  and replace the stratum port you want, default is 3339 listening on localhost/0.0.0.0

- change workername_modifier: "my_workername_replace" with your upstream pool username

- change workername_override: "myworker" with the worker name you want the proxy to use on the miners behalf

-set max connections,  this is set default to 100, you can change this to your mining setup, this will be hardware dependant on the computer running the proxy

- you can also set the log level
remeber set to one of the following values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', or 'CRITICAL'. If an invalid log level is specified or the key is missing, the default log level 'WARNING' will be used.

- change 


pip install pyyaml

--To Run-

bash:  python3 python_stratum3.py

-List of features -
apply extra naunce if upstream pool requires it

NO DEV FEES'  ( I didnt find a working python 3 stratum proxy so I wrote this.


