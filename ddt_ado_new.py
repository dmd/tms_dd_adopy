import os
import sys
import random

from pathlib import Path
from enum import Enum
import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
import pandas as pd

from datetime import datetime
from psychopy import core, visual, event, data, gui, prefs
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from adopy.tasks.dd import TaskDD, ModelHyp
from adopy import Engine

PATH_ROOT = Path(__file__).absolute().parent
PATH_DATA = PATH_ROOT / 'data'
PATH_IMAGE = PATH_ROOT / 'images'

#prefs.general['audioLib'] = ['pyo']
class DdtDrawer:
    """PsychoPy drawer for the choice under risk and ambiguity task."""

    def __init__(self,
                 window: visual.Window,
                 box_w: float = 6,
                 box_h: float = 6,
                 dist_btwn: float = 8,
                 text_font: str = 'NanumGothic',
                 text_size: int = 1,
                 text_margin: float = 1,
                 fixation_size: float = 1,
                 pos_x: float = 0,
                 pos_y: float = 0,
                 ):
        self.window = window
        self.box_w = box_w
        self.box_h = box_h
        self.dist_btwn = dist_btwn
        self.text_font = text_font
        self.text_size = text_size
        self.text_margin = text_margin
        self.fixation_size = fixation_size
        self.pos_x = pos_x
        self.pos_y = pos_y

        with open(PATH_ROOT / 'instructions.yml', 'r', encoding='utf-8') as f:
            self.instructions = yaml.load(f, Loader=Loader)

    @staticmethod
    def convert_delay_to_str(delay):
        tbl_conv = {
            0: 'Now',
            0.43: '3 days later',
            0.714: '5 days later',
            1: '1 week later',
            2: '2 weeks later',
            3: '3 weeks later',
            4.3: '1 month later',
            6.44: '6 weeks later',
            8.6: '2 months later',
            10.8: '10 weeks later',
            12.9: '3 months later',
            17.2: '4 months later',
            21.5: '5 months later',
            26: '6 months later',
            52: '1 year later',
            104: '2 years later',
            156: '3 years later',
            260: '5 years later',
            520: '10 years later'
        }
        mv, ms = None, None
        for (v, s) in tbl_conv.items():
            if mv is None or np.square(delay - mv) > np.square(delay - v):
                mv, ms = v, s
        return ms

    def draw_option(self, delay, amount, direction=1, chosen=False):
        pos_x_center = self.pos_x + direction * self.dist_btwn
        pos_x_left = pos_x_center - self.box_w
        pos_x_right = pos_x_center + self.box_w
        pos_y_top = self.pos_y + self.box_h / 2
        pos_y_bottom = self.pos_y - self.box_h / 2

        vertices = (
            (pos_x_left, pos_y_top),
            (pos_x_right, pos_y_top),
            (pos_x_right, pos_y_bottom),
            (pos_x_left, pos_y_bottom)
        )

        box = visual.ShapeStim(
            self.window,
            lineWidth=12 if chosen else 8,
            lineColor='white',
            fillColor='darkgreen' if chosen else 'black',
            vertices=vertices,
        )
        box.draw()

        text_a = visual.TextStim(
            self.window,
            '$ {:,.0f}'.format(amount),
            font=self.text_font,
            pos=(pos_x_center, self.pos_y + self.text_margin),
        )
        text_a.size = self.text_size
        text_a.draw()

        text_d = visual.TextStim(
            self.window,
            self.convert_delay_to_str(delay),
            font=self.text_font,
            pos=(pos_x_center, self.pos_y - self.text_margin),
        )
        text_d.size = self.text_size
        text_d.draw()

    def draw(self, t_ss, t_ll, r_ss, r_ll, direction, chosen=None):
        if direction == 1:
            d_ss, d_ll = -1, 1
        else:
            d_ss, d_ll = 1, -1

        self.draw_option(t_ss, r_ss, d_ss, chosen == 1)  # SS
        self.draw_option(t_ll, r_ll, d_ll, chosen == 0)  # LL

    def draw_fixation(self):
        fixation = visual.GratingStim(
            self.window,
            color='white',
            tex=None,
            mask='cross',
            size=self.fixation_size,
        )
        fixation.draw()

    def draw_intro(self):
        text = visual.TextStim(
            self.window,
            self.instructions['intro'],
            font=self.text_font,
            pos=(0, 0),
            wrapWidth=30,
            anchorVert='center')
        text.draw()

    def draw_train_before(self, page):
        if page == 0:
            tmppos = (self.pos_x, self.pos_y)
            self.pos_x, self.pos_y = 0, -2 * self.text_margin
            self.draw(0, 52, 100, 800, 1)
            self.pos_x, self.pos_y = tmppos

            text = visual.TextStim(
                self.window,
                self.instructions['train_before'][0],
                font=self.text_font,
                pos=(0, self.box_h / 2 + 1 * self.text_margin),
                wrapWidth=30,
            )
            text.size = self.text_size
            text.draw()

        elif page == 1:
            tmppos = (self.pos_x, self.pos_y)
            self.pos_x, self.pos_y = 0, -2 * self.text_margin
            self.draw(0, 52, 100, 800, 1)
            self.pos_x, self.pos_y = tmppos

            text = visual.TextStim(
                self.window,
                self.instructions['train_before'][1],
                font=self.text_font,
                pos=(0, self.box_h / 2 + 1 * self.text_margin),
                wrapWidth=30,
            )
            text.size = self.text_size
            text.draw()

        elif page == 2:
            tmppos = (self.pos_x, self.pos_y)
            self.pos_x, self.pos_y = 0, -2 * self.text_margin
            self.draw(0, 52, 100, 800, 1)
            self.pos_x, self.pos_y = tmppos

            text = visual.TextStim(
                self.window,
                self.instructions['train_before'][2],
                font=self.text_font,
                pos=(0, self.box_h / 2 + 1 * self.text_margin),
                wrapWidth=30,
            )
            text.size = self.text_size
            text.draw()

        elif page == 3:
            text = visual.TextStim(
                self.window,
                self.instructions['train_before'][3],
                font=self.text_font,
                pos=(0, 0),
                wrapWidth=30,
            )
            text.size = self.text_size
            text.draw()

        else:
            raise ValueError('Invalid page number for instructions.')

    def draw_train_after(self):
        text = visual.TextStim(
            self.window,
            self.instructions['train_after'],
            font=self.text_font,
            pos=(0, 0),
            wrapWidth=30,
            anchorVert='center')
        text.draw()

    def draw_main_before(self, block, n_trial):
        text = visual.TextStim(
            self.window,
            self.instructions['main_before'].format(n_trial),
            font=self.text_font,
            pos=(0, 0),
            wrapWidth=30,
            anchorVert='center')
        text.draw()

    # def draw_main_after(self, block):
    #     text = visual.TextStim(
    #         self.window,
    #         self.instructions['main_after'].format(block),
    #         font=self.text_font,
    #         pos=(0, 0),
    #         wrapWidth=30,
    #         anchorVert='center')
    #     text.draw()

    def draw_outro(self):
        text = visual.TextStim(
            self.window,
            self.instructions['outro'],
            font=self.text_font,
            pos=(0, 0),
            wrapWidth=30,
            anchorVert='center')
        text.draw()


def make_grid(start, end, n):
    return np.linspace(start, end, n + 1, endpoint=False)[1:]


def make_grid_log(a, b, n):
    return np.logspace(np.log10(a), np.log10(b), n + 1, endpoint=False)[1:]


class DdtRunner:
    def __init__(self, window, drawer, subj, path_output):
        self.window = window
        self.drawer = drawer
        self.subj = subj
        self.path_output = path_output
        if os.path.exists(path_output):
            self.df = pd.read_table(path_output, sep='\t')
        else:
            self.df = pd.DataFrame(None)

        self.task = TaskDD()
        self.model = ModelHyp()
        self.grid_response = {'choice': [0, 1]}
        self. engine = Engine(
            task=self.task,
            model=self.model,
            grid_design=self.generate_grid_designs(),
            grid_param=self.generate_grid_params(),
            grid_response=self.grid_response)

    def save_record(self):
        columns=[
            'subject', 'block', 'block_type', 'trial',
            *(self.task.designs),'resp_ss', 'rt',
            *['mean_' + p for p in self.model.params],
            *['sd_' + p for p in self.model.params],
        ]
        self.df[columns].to_csv(self.path_output, sep='\t', index=False)

    @staticmethod
    def generate_grid_designs():
        # Amounts of rewards
        am_soon = np.arange(10, 790, 10)
        am_late = [800]

        amounts = np.vstack([
            (ams, aml) for ams in am_soon for aml in am_late if ams < aml
        ])

        # Delays
        t_ss = [0]
        t_ll = [
            0.43, 0.714, 1, 2, 3,
            4.3, 6.44, 8.6, 10.8, 12.9,
            17.2, 21.5, 26, 52, 104,
            156, 260, 520
        ]

        delays = np.vstack([
            (ds, dl) for ds in t_ss for dl in t_ll if ds < dl
        ])

        designs = {('t_ss', 't_ll'): delays, ('r_ss', 'r_ll'): amounts}
        return designs

    @staticmethod
    def generate_grid_params():
        k = make_grid_log(0.0001, 10, 50)
        tau = make_grid(0, 5, 50)

        # k: discounting rate parameter
        # tau: inverse temperature parameter

        params = {'k': k, 'tau': tau}
        return params

    def show_countdown(self):
        text1 = visual.TextStim(self.window, text="1",
                                pos=(0.0, 0.0), height=2)
        text2 = visual.TextStim(self.window, text="2",
                                pos=(0.0, 0.0), height=2)
        text3 = visual.TextStim(self.window, text="3",
                                pos=(0.0, 0.0), height=2)

        text3.draw()
        self.window.flip()
        core.wait(1)

        text2.draw()
        self.window.flip()
        core.wait(1)

        text1.draw()
        self.window.flip()
        core.wait(1)

    def show_intro(self):
        self.drawer.draw_intro()
        self.window.flip()
        _ = event.waitKeys(keyList=['space', 'return'])

    def show_outro(self):
        self.drawer.draw_outro()
        self.window.flip()
        _ = event.waitKeys(keyList=['space', 'return'])

    def show_block_start(self, block, n_trial):
        self.drawer.draw_main_before(block, n_trial)
        self.window.flip()
        _ = event.waitKeys(keyList=['space', 'return'])

    # def show_block_end(self, block):
    #     self.drawer.draw_main_after(block)
    #     self.window.flip()
    #     _ = event.waitKeys(keyList=['space', 'return'])

    def run_trial(self, design):
        self.drawer.draw_fixation()
        self.window.flip()
        core.wait(1)

        # Direction: 0 (L - LL / R - SS) or
        #            1 (L - SS / R - LL)
        direction = int(np.random.randint(0, 2))

        self.drawer.draw(design['t_ss'], design['t_ll'],
                         design['r_ss'], design['r_ll'],
                         direction)
        self.window.flip()
        timer = core.Clock()
        keys = event.waitKeys(keyList=['z', 'slash', 'm'])
        rt = timer.getTime()

        resp_left = int(keys[0] == 'z')
        # 1 if chosen left, 0 if chosen right option
        resp_ss = int((1 - resp_left) ^ (direction == 1))
        # 1 if chosen SS option, 0 if chosen LL option
        self.drawer.draw(design['t_ss'], design['t_ll'],
                         design['r_ss'], design['r_ll'],
                         direction, resp_ss)
        self.window.flip()
        
        if 'escape' in event.getKeys(): #press esc and select an option to close the task
            print("escape exit")
            self.window.close()
            #sys.exit(0)
            core.quit()

        core.wait(1)

        return resp_ss, rt

    def run_train_block(self, n_trial=10):
        """Run a block for training purpose."""
        for i in range(4):
            self.drawer.draw_train_before(i)
            self.window.flip()
            _ = event.waitKeys(keyList=['space', 'return'])

        self.show_countdown()
        for trial in range(n_trial):
            design = self.engine.get_design('random')
            # print(trial, design)
            _ = self.run_trial(design)

        self.drawer.draw_train_after()
        self.window.flip()
        _ = event.waitKeys(keyList=['space', 'return'])

    def run_block(self, block, block_type, n_trial=60):
        """Run a block with optimal designs chosen by ADO."""
        self.engine.reset()

        self.show_countdown()
        for trial in range(n_trial):
            if block_type == 'fixed':
                design = self.engine.get_design('random')
            else:
                design = self.engine.get_design('optimal')

            resp_ss, rt = self.run_trial(design)
            resp_ll = 1 - resp_ss
            self.engine.update(design, resp_ll)
            
            dict_mean = {
                'mean_' + p: m
                for p, m in zip(self.model.params, self.engine.post_mean)
            }
            dict_sd = {
                'sd_' + p: m
                for p, m in zip(self.model.params, self.engine.post_sd)
            }            

            self.df = self.df.append(pd.Series({
                'subject': self.subj,
                'block': block,
                'block_type': block_type,
                'trial': trial + 1,
                **design,
                'resp_ss': resp_ss,
                'rt': rt,
                **dict_mean,
                **dict_sd
            }), ignore_index=True)

            self.save_record()


def main():
    # OS specific settings
    if os.name == 'nt':
        text_font = 'NanumGothic'
    else:
        text_font = 'Nanum Gothic'

    # Show an information dialog
    info = {
        'Date': data.getDateStr('%Y/%m/%d'),
        'Subject ID': 0,
        'Session': 1,
        'Number of trials': 20,
        'Number of train trials': 5,
        'Show tutorial': True,
    }

    dialog = gui.DlgFromDict(
        info,
        title='Subject information',
        order=[
#            'Date',
            'Subject ID',
            'Session',
            'Number of trials',
            'Number of train trials',
            'Show tutorial'],
        fixed=['Data'])

    if not dialog.OK:
        core.quit()

    subj = info['Subject ID']
    session = info['Session']
    n_block = 1
    n_trial = info['Number of trials']
    n_train_trial = info['Number of train trials']
    has_tutorial = info['Show tutorial']

    time_now = datetime.now()
    time_now_iso = time_now.isoformat().replace(
        ':', '-').replace('T', '-')[:-7]
    
    # Save Data
    fn_data = 'DDT{subj:03d}_ses{session:01d}_{time_now_iso}.csv'.format(
        subj=subj, session=session, time_now_iso=time_now_iso)
    PATH_DATA.mkdir(exist_ok=True)
    path_output = str(PATH_DATA / fn_data)

    # Open a window
    window = visual.Window(size=[1920, 1080],
                           units='deg',
                           monitor='testMonitor',
                           color='black',
                           screen=1,
                           allowGUI=False,
                           fullscr=True)
    #event.globalKeys.add(key='escape', func=core.quit, name='shutdown')
    
    block_types = ['ado']

    print('Block types:', block_types)

    # Initialize a drawer and a runner
    drawer = DdtDrawer(window, text_font=text_font)
    runner = DdtRunner(window, drawer, subj, path_output)

    # Run blocks
    if has_tutorial:
        runner.show_intro()
        runner.run_train_block(n_train_trial)

    for block, block_type in enumerate(block_types):
        runner.show_block_start(block + 1, n_trial)
        runner.run_block(block + 1, block_type, n_trial)
        #runner.show_block_end(block + 1)

    runner.show_outro()
    window.close()
    core.quit()

if __name__ == '__main__':
    main()
