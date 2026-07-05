# -*- coding: utf-8 -*-
"""Kernel methods for Abaqus three-point bending plugin."""

from abaqus import mdb
from abaqusConstants import THREE_D, DEFORMABLE_BODY


def build_three_point_bending(
    length=100.0,
    width=10.0,
    height=10.0,
    support_span=80.0,
    indenter_radius=5.0,
):
    model_name = "Model-1"
    if model_name not in mdb.models:
        mdb.Model(name=model_name)

    model = mdb.models[model_name]

    sketch = model.ConstrainedSketch(name="__profile__", sheetSize=max(length, width) * 2.0)
    sketch.rectangle(point1=(0.0, 0.0), point2=(length, height))

    part_name = "Specimen"
    if part_name in model.parts:
        del model.parts[part_name]

    part = model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidExtrude(sketch=sketch, depth=width)

    del model.sketches["__profile__"]

    print("Three-point bending specimen created:")
    print("  length=", length)
    print("  width=", width)
    print("  height=", height)
    print("  support_span=", support_span)
    print("  indenter_radius=", indenter_radius)
