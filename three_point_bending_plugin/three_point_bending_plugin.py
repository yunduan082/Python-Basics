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
    DIALOG_ACTIONS_SEPARATOR,
    getAFXApp,
)


class TPBForm(AFXForm):
    def __init__(self, owner):
        super(TPBForm, self).__init__(owner)
        self.cmd = AFXGuiCommand(self, "build_three_point_bending", "tpb_kernel")
        self.length_kw = AFXFloatKeyword(self.cmd, "length", True, 127.0)
        self.width_kw = AFXFloatKeyword(self.cmd, "width", True, 12.7)
        self.height_kw = AFXFloatKeyword(self.cmd, "height", True, 3.2)
        self.support_span_kw = AFXFloatKeyword(self.cmd, "support_span", True, 51.2)
        self.support_radius_kw = AFXFloatKeyword(self.cmd, "support_radius", True, 5.0)
        self.indenter_radius_kw = AFXFloatKeyword(self.cmd, "indenter_radius", True, 5.0)
        self.loading_displacement_kw = AFXFloatKeyword(
            self.cmd, "loading_displacement", True, 5.0
        )
        self.mesh_size_kw = AFXFloatKeyword(self.cmd, "mesh_size", True, 1.0)

    def getFirstDialog(self):
        return TPBDialog(self)


class TPBDialog(AFXDataDialog):
    def __init__(self, form):
        super(TPBDialog, self).__init__(
            form,
            "Three-Point Bending Plugin",
            self.OK | self.CANCEL,
            DIALOG_ACTIONS_SEPARATOR,
        )

        AFXTextField(
            p=self,
            ncols=16,
            labelText="Sample length (mm):",
            tgt=form.length_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Sample width (mm):",
            tgt=form.width_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Sample thickness (mm):",
            tgt=form.height_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Support span (mm):",
            tgt=form.support_span_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Support radius (mm):",
            tgt=form.support_radius_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Indenter radius (mm):",
            tgt=form.indenter_radius_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Loading disp. (mm):",
            tgt=form.loading_displacement_kw,
            sel=0,
        )
        AFXTextField(
            p=self,
            ncols=16,
            labelText="Mesh size (mm):",
            tgt=form.mesh_size_kw,
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
            description="Builds an ASTM D790 ABS three-point bending model.",
            helpUrl="",
        )


def registerPlugin():
    TPBPlugin().register()