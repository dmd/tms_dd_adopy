** Task instruction **
- Install the required dependencies: pip install -r requirements.txt
- Run "python ddt_web.py" and open http://localhost:5050/ in your browser
- The form automatically assigns the next available 4-digit subject ID starting from 1001
- All form fields are locked to prevent accidental changes during data collection
- Supports setup via query parameters for automated configuration

** Features **
- Web-based delayed discounting task with adaptive design optimization (ADO)
- Instant crosshairs feedback for improved user experience
- Automatic subject ID assignment based on existing data files
- Form lockdown and setup parameter support for research automation
- Tutorial mode with configurable training trials

** Setup Parameters **
You can configure the experiment via URL parameters:
- Individual parameters: ?subject_id=1001&session=1&num_train_trials=5&num_main_trials=40&show_tutorial=1
- Setup parameter (5 comma-separated values): ?setup=1001,1,5,40,1

** Controls **
- Press 'z' to choose the left option
- Press 'm' or '/' to choose the right option
- In instruction screens, press <space> or <Enter> to proceed

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
