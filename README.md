# nbs-course-selection-webapp
This project is an interactive web application where students can input their interests and use an Integer Optimization model to get the suggested course list for the academic year. The mathematical model is made up of Python RSOME and Gurobi. More detail is indicated in model.py file under webapp folder. The web application is made up of Python Flask, JavaScript and HTML.

The information of all courses can be found on Nanyang Business School website: http://web.nbs.ntu.edu.sg/undergrad/common/contents/courselist.asp

There are 4 main screens: Select (Homepage), Optimize, Result and Reference. The model will run on back-end after triggering Optimize, and output will be sent back to front-end by View Result.
 
![demo1](https://github.com/QuanPham19/nbs-course-selection-webapp/assets/106662700/9825ddfe-6a6f-49ea-b84e-5be2cf8152b9)

![demo2](https://github.com/QuanPham19/nbs-course-selection-webapp/assets/106662700/255e2bc3-1bb3-45e1-acbe-f463f887e3a5)

![demo3](https://github.com/QuanPham19/nbs-course-selection-webapp/assets/106662700/25ab5b69-bbb3-4286-9619-6226efd46248)
