** Task instruction **
- First, install PsychoPy (https://www.psychopy.org/download.html) and ADOpy (from GitHub: https://github.com/adopy/adopy, version 0.4.1)
- Run "ddt_ado_new.py" on a Python console to start the task.
- Modify the participant ID and the number of trials in the subject information box as desired.
- Alternatively, to run a web-based interface (no PsychoPy required), install Flask (pip install flask), then run "python ddt_web.py" and open http://localhost:5050/ in your browser.

In the instruction screen, press <space> to proceed to the next screen.
You may revise "instructions.yml" to change the instructions.

Press <esc> before making a choice if you want to immediately close the task.

** Data format **
Data are saved in csv format.
The columns in a csv file will be as below:

-subject: subject code
-block: block number
-block_type: fixed as ado in this task
-trial: trial number
-t_ss: delay of shorter-smaller option (always zero)
-t_ll: delay of longer-larger option (in weeks)
-r_ss: amount of shorter-smaller reward
-r_ll: amount of longer-larger reward
-resp_ss: response in the trial (0 = ll, 1 = ss)
-rt: response time (in seconds)
-mean_k: posterior mean of the delay discounting rate parameter (hyperbolic model)
-mean_tau: posterior mean of the tau parameter
-sd_k: standard deviation of the delay discounting rate parameter
-sd_tau: standard deviation of the tau parameter
