This folder contains all the files needed to run a global sensitivity analysis on the DAFNI platform using the Hymod hydroloigcal model and tools from the SAFEtoolbox. This process has three main steps, (1) dockerise the HyMod model, (2) run it on DAFNI and (3) carry out a simple sensitivity analysis on the results. 

To Dockerside the model you need: 
1) The Dockerfile
2) The requirements.txt file which is drawn on by the Dockerfile 
3) The scripts needed to run the model (run.py, util.py and HyMod.py) 

To upload and run the model on DAFNI you need: 
1) The model definition file
2) The input data file LeafCatch.txt

To carry out a simple sensiivity analysis the GSA_PAWN.ipynb can be run in the visualisation part of a DAFNI worflow. 

![Flow Chart](flow_chart.png)


