##easy automation test

This library is to help developer or tester write automation
 testcases faster and easier. Include web, api, Android and iOS.
 For web UI automation basic framework depends on selenium, Api 
 test depends on requests library and mobile UI automaton test
 depends on Appium. 
 
 ## basic command
 easy-automation -h
 you can watch all command help.
 
 position param:
 - startWebProject/ startApiProject/ startAndroidProject/ startIosProject
 - projectName
 
 example: easy-automation startWebproject web_project_name
 
 you can create a new project quickly by execute this command.
 just like django create project/app, it will auto create project
 directory structure.

 ## basic module
 - core:
 
 This module include all base class. base_appium, base_page
 and base_request. It is mainly responsible for init test
 driver and environment.
 
 - contrib
 
 This module provide some mixin class to help write page class,
 that encapsulation some basic selenium or appium find method,
  make them easier and more efficient.
  
 - utils
 
 This module provide some util class, like custom_logging, 
 custom_faker, yaml_loader, you can quick prepare test data
 or record test log by them.
 
 
 
 
 
 