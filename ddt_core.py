"""Headless core logic for the DDT ADO experiment, decoupled from PsychoPy."""
import os
from pathlib import Path

import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
import pandas as pd
from adopy.tasks.dd import TaskDD, ModelHyp
from adopy import Engine


def make_grid(start, end, n):
    return np.linspace(start, end, n + 1, endpoint=False)[1:]


def make_grid_log(a, b, n):
    return np.logspace(np.log10(a), np.log10(b), n + 1, endpoint=False)[1:]


class DdtCore:
    """Headless core experiment logic for ADO-based DDT task."""

    def __init__(self, subject, session, path_output):
        self.subject = subject
        self.session = session
        self.path_output = Path(path_output)
        self.path_output.parent.mkdir(exist_ok=True)
        self.task = TaskDD()
        self.model = ModelHyp()
        self.engine = Engine(
            task=self.task,
            model=self.model,
            grid_design=self.generate_grid_designs(),
            grid_param=self.generate_grid_params(),
            grid_response={'choice': [0, 1]},
        )
        self.df = pd.DataFrame()
        self.block = 1
        self.block_type = 'ado'

    @staticmethod
    def generate_grid_designs():
        am_soon = np.arange(10, 790, 10)
        am_late = [800]
        amounts = np.vstack(
            [(ams, aml) for ams in am_soon for aml in am_late if ams < aml]
        )
        t_ss = [0]
        t_ll = [
            0.43, 0.714, 1, 2, 3,
            4.3, 6.44, 8.6, 10.8, 12.9,
            17.2, 21.5, 26, 52, 104,
            156, 260, 520,
        ]
        delays = np.vstack(
            [(ds, dl) for ds in t_ss for dl in t_ll if ds < dl]
        )
        return {('t_ss', 't_ll'): delays, ('r_ss', 'r_ll'): amounts}

    @staticmethod
    def generate_grid_params():
        k = make_grid_log(0.0001, 10, 50)
        tau = make_grid(0, 5, 50)
        return {'k': k, 'tau': tau}

    def get_design(self, mode='optimal'):
        design = self.engine.get_design(mode)
        return {k: float(v) for k, v in design.items()}

    def update_and_record(self, design, resp_ss, rt):
        resp_ll = 1 - resp_ss
        self.engine.update(design, resp_ll)
        means = {'mean_' + p: m for p, m in zip(self.model.params, self.engine.post_mean)}
        sds = {'sd_' + p: m for p, m in zip(self.model.params, self.engine.post_sd)}
        trial = len(self.df) + 1
        row = {
            'subject': self.subject,
            'block': self.block,
            'block_type': self.block_type,
            'trial': trial,
            **design,
            'resp_ss': resp_ss,
            'rt': rt,
            **means,
            **sds,
        }
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)

    def save_record(self):
        cols = [
            'subject', 'block', 'block_type', 'trial',
            *self.task.designs,
            'resp_ss', 'rt',
            *['mean_' + p for p in self.model.params],
            *['sd_' + p for p in self.model.params],
        ]
        self.df[cols].to_csv(self.path_output, sep='\t', index=False)