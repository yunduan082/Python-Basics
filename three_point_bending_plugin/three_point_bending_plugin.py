# -*- coding: utf-8 -*-
"""
Abaqus/CAE Plugin: Three-point bending model builder
Target: Abaqus 2025 + Python 3
"""

from abaqusGui import (
    AFXMode,
    AFXDataDialog,
    AFXFloatKeyword,
    AFXForm,
    AFXGuiCommand,
    AFXTextField,
    getAFXApp,
)
class TPBForm(AFXForm):
    def __init__(self, owner):
        super(TPBForm, self).__init__(owner)
        self.cmd = AFXGuiCommand(self, "build_three_point_bending", "tpb_kernel")
        self.length_kw = AFXFloatKeyword(self.cmd, "length", True, 100.0)
        self.width_kw = AFXFloatKeyword(self.cmd, "width", True, 10.0)
        self.height_kw = AFXFloatKeyword(self.cmd, "height", True, 10.0)
        self.support_span_kw = AFXFloatKeyword(self.cmd, "support_span", True, 80.0)
        self.indenter_radius_kw = AFXFloatKeyword(self.cmd, "indenter_radius", True, 5.0)

    def getFirstDialog(self):
        return TPBDialog(self)


class TPBDialog(AFXDataDialog):
    def __init__(self, form):
        super(TPBDialog, self).__init__(form, "Three-Point Bending Plugin")

        AFXTextField(
            p=self,
            ncols=16,
            labelText="Specimen length:",
            tgt=form.length_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Specimen width:",
            tgt=form.width_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Specimen height:",
            tgt=form.height_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Support span:",
            tgt=form.support_span_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Indenter radius:",
            tgt=form.indenter_radius_kw,
            sel=0,
        )


class TPBPlugin:
    def __init__(self):
        self.toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
        self.form = TPBForm(self.toolset)

    def register(self):
        self.toolset.registerGuiMenuButton(
            buttonText="Three-Point Bending...",
            object=self.form,
            kernelInitString="import tpb_kernel",
            messageId=AFXMode.ID_ACTIVATE,
            icon=None,
            applicableModules=("Part",),
            version="2025",
            author="Auto-generated",
            description="Builds a base specimen part for 3-point bending.",
            helpUrl="",
        )


def registerPlugin():
    TPBPlugin().register()
