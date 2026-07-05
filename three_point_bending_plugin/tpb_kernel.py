# -*- coding: utf-8 -*-
"""Kernel methods for the Abaqus three-point bending plugin."""

from abaqus import mdb
from abaqusConstants import (
    ANALYSIS,
    C3D8R,
    CARTESIAN,
    DEFAULT,
    DEFORMABLE_BODY,
    DISCRETE_RIGID_SURFACE,
    FINITE,
    FRICTIONLESS,
    FROM_SECTION,
    HARD,
    MIDDLE_SURFACE,
    NONE,
    ODB,
    OFF,
    ON,
    PERCENTAGE,
    R3D3,
    R3D4,
    SINGLE,
    STANDARD,
    THREE_D,
    UNIFORM,
    UNSET,
)
import mesh
import regionToolset


MODEL_NAME = "TPB_ABS_ASTMD790_Model"
JOB_NAME = "TPB_ABS_ASTMD790"


ABS_PLASTIC_TABLE = (
    (40.0, 0.000),
    (43.0, 0.010),
    (45.0, 0.025),
    (46.0, 0.050),
    (44.0, 0.100),
)


def _validate_inputs(
    length,
    width,
    height,
    support_span,
    support_radius,
    indenter_radius,
    loading_displacement,
    mesh_size,
):
    values = {
        "length": length,
        "width": width,
        "height": height,
        "support_span": support_span,
        "support_radius": support_radius,
        "indenter_radius": indenter_radius,
        "loading_displacement": loading_displacement,
        "mesh_size": mesh_size,
    }
    for name, value in values.items():
        if value <= 0.0:
            raise ValueError("%s must be greater than zero." % name)

    if support_span >= length:
        raise ValueError("support_span must be smaller than sample length.")


def _new_model():
    if MODEL_NAME in mdb.models:
        del mdb.models[MODEL_NAME]
    return mdb.Model(name=MODEL_NAME)


def _make_sample_part(model, length, width, height, mesh_size):
    sketch = model.ConstrainedSketch(name="__sample_profile__", sheetSize=length * 1.5)
    sketch.rectangle(point1=(-length / 2.0, -height / 2.0), point2=(length / 2.0, height / 2.0))

    part = model.Part(name="Sample", dimensionality=THREE_D, type=DEFORMABLE_BODY)
    part.BaseSolidExtrude(sketch=sketch, depth=width)
    del model.sketches["__sample_profile__"]

    material = model.Material(name="ABS_Elastic_Plastic")
    material.Elastic(table=((2200.0, 0.35),))
    material.Plastic(table=ABS_PLASTIC_TABLE)

    model.HomogeneousSolidSection(name="ABS_Section", material="ABS_Elastic_Plastic", thickness=None)
    region = regionToolset.Region(cells=part.cells)
    part.SectionAssignment(
        region=region,
        sectionName="ABS_Section",
        offset=0.0,
        offsetType=MIDDLE_SURFACE,
        offsetField="",
        thicknessAssignment=FROM_SECTION,
    )

    elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
    part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
    part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    return part


def _make_rigid_cylinder_part(model, name, radius, rigid_width, mesh_size):
    sketch = model.ConstrainedSketch(name="__%s_profile__" % name, sheetSize=radius * 6.0)
    sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(radius, 0.0))

    part = model.Part(name=name, dimensionality=THREE_D, type=DISCRETE_RIGID_SURFACE)
    part.BaseShellExtrude(sketch=sketch, depth=rigid_width)
    rp_feature = part.ReferencePoint(point=(0.0, 0.0, rigid_width / 2.0))
    part.Set(name="RP", referencePoints=(part.referencePoints[rp_feature.id],))
    del model.sketches["__%s_profile__" % name]

    quad = mesh.ElemType(elemCode=R3D4, elemLibrary=STANDARD)
    tri = mesh.ElemType(elemCode=R3D3, elemLibrary=STANDARD)
    part.setElementType(regions=(part.faces,), elemTypes=(quad, tri))
    part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()
    return part


def _assembly_surface(assembly, instance_name, surface_name):
    instance = assembly.instances[instance_name]
    assembly.Surface(name=surface_name, side1Faces=instance.faces)
    return assembly.surfaces[surface_name]


def _add_instance_rp_set(assembly, instance_name, set_name):
    instance = assembly.instances[instance_name]
    reference_points = tuple(instance.referencePoints.values())
    if not reference_points:
        raise RuntimeError("Rigid instance %s has no reference point." % instance_name)
    assembly.Set(name=set_name, referencePoints=reference_points)
    return assembly.sets[set_name]


def build_three_point_bending(
    length=127.0,
    width=12.7,
    height=3.2,
    support_span=51.2,
    support_radius=5.0,
    indenter_radius=5.0,
    loading_displacement=5.0,
    mesh_size=1.0,
):
    """Create a ready-to-submit ASTM D790 three-point bending model.

    Units are mm, N, MPa. The default specimen follows the common ASTM D790
    rectangular bar geometry: 127 x 12.7 x 3.2 mm with a 16:1 support span.
    """
    _validate_inputs(
        length,
        width,
        height,
        support_span,
        support_radius,
        indenter_radius,
        loading_displacement,
        mesh_size,
    )

    model = _new_model()
    rigid_width = width + 2.0 * max(mesh_size, 1.0)

    sample = _make_sample_part(model, length, width, height, mesh_size)
    support = _make_rigid_cylinder_part(model, "Support", support_radius, rigid_width, mesh_size)
    indenter = _make_rigid_cylinder_part(model, "Loading_Nose", indenter_radius, rigid_width, mesh_size)

    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)

    assembly.Instance(name="Sample-1", part=sample, dependent=ON)
    assembly.translate(instanceList=("Sample-1",), vector=(0.0, 0.0, -width / 2.0))

    assembly.Instance(name="Support_Left-1", part=support, dependent=ON)
    assembly.Instance(name="Support_Right-1", part=support, dependent=ON)
    assembly.Instance(name="Loading_Nose-1", part=indenter, dependent=ON)

    z_shift = -rigid_width / 2.0
    assembly.translate(
        instanceList=("Support_Left-1",),
        vector=(-support_span / 2.0, -height / 2.0 - support_radius, z_shift),
    )
    assembly.translate(
        instanceList=("Support_Right-1",),
        vector=(support_span / 2.0, -height / 2.0 - support_radius, z_shift),
    )
    assembly.translate(
        instanceList=("Loading_Nose-1",),
        vector=(0.0, height / 2.0 + indenter_radius, z_shift),
    )

    _assembly_surface(assembly, "Sample-1", "Sample_Surface")
    _assembly_surface(assembly, "Support_Left-1", "Support_Left_Surface")
    _assembly_surface(assembly, "Support_Right-1", "Support_Right_Surface")
    _assembly_surface(assembly, "Loading_Nose-1", "Loading_Nose_Surface")

    rp_support_left = assembly.instances["Support_Left-1"].sets["RP"]
    rp_support_right = assembly.instances["Support_Right-1"].sets["RP"]
    rp_loading_nose = assembly.instances["Loading_Nose-1"].sets["RP"]

    contact_property = model.ContactProperty("Frictionless_Contact")
    contact_property.NormalBehavior(
        pressureOverclosure=HARD,
        allowSeparation=ON,
        constraintEnforcementMethod=DEFAULT,
    )
    contact_property.TangentialBehavior(formulation=FRICTIONLESS)

    for name, master_surface in (
        ("Contact_Left_Support", assembly.surfaces["Support_Left_Surface"]),
        ("Contact_Right_Support", assembly.surfaces["Support_Right_Surface"]),
        ("Contact_Loading_Nose", assembly.surfaces["Loading_Nose_Surface"]),
    ):
        model.SurfaceToSurfaceContactStd(
            name=name,
            createStepName="Initial",
            main=master_surface,
            secondary=assembly.surfaces["Sample_Surface"],
            sliding=FINITE,
            thickness=ON,
            interactionProperty="Frictionless_Contact",
            adjustMethod=NONE,
        )

    model.StaticStep(
        name="Bending",
        previous="Initial",
        nlgeom=ON,
        initialInc=0.01,
        minInc=1.0e-8,
        maxInc=0.05,
        maxNumInc=200,
    )

    model.EncastreBC(
        name="BC_Support_Left_Fixed",
        createStepName="Initial",
        region=rp_support_left,
    )
    model.EncastreBC(
        name="BC_Support_Right_Fixed",
        createStepName="Initial",
        region=rp_support_right,
    )
    model.DisplacementBC(
        name="BC_Loading_Nose_Displacement",
        createStepName="Initial",
        region=rp_loading_nose,
        u1=0.0,
        u2=UNSET,
        u3=0.0,
        ur1=0.0,
        ur2=0.0,
        ur3=0.0,
        amplitude=UNSET,
        fixed=OFF,
        distributionType=UNIFORM,
        fieldName="",
        localCsys=None,
    )
    model.boundaryConditions["BC_Loading_Nose_Displacement"].setValuesInStep(
        stepName="Bending",
        u2=-abs(loading_displacement),
    )

    if "F-Output-1" in model.fieldOutputRequests:
        model.fieldOutputRequests["F-Output-1"].setValues(
            variables=("S", "E", "PE", "PEEQ", "U", "RF", "CF", "CSTRESS", "CDISP")
        )
    if "H-Output-1" in model.historyOutputRequests:
        del model.historyOutputRequests["H-Output-1"]
    model.HistoryOutputRequest(
        name="Loading_Nose_RF_U",
        createStepName="Bending",
        variables=("U2", "RF2"),
        region=rp_loading_nose,
    )

    if JOB_NAME in mdb.jobs:
        del mdb.jobs[JOB_NAME]
    mdb.Job(
        name=JOB_NAME,
        model=MODEL_NAME,
        description="ASTM D790 three-point bending model for ABS. Created by plugin; submit manually.",
        type=ANALYSIS,
        atTime=None,
        waitMinutes=0,
        waitHours=0,
        queue=None,
        memory=90,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE,
        echoPrint=OFF,
        modelPrint=OFF,
        contactPrint=OFF,
        historyPrint=OFF,
        userSubroutine="",
        scratch="",
        resultsFormat=ODB,
        numCpus=4,
        numDomains=4,
        numGPUs=0,
    )

    print("Created ASTM D790 ABS three-point bending model.")
    print("  Model: %s" % MODEL_NAME)
    print("  Job:   %s (not submitted)" % JOB_NAME)
    print("  Parts: Sample, Support x2 instances, Loading_Nose")
    print("  Dimensions: %.4g x %.4g x %.4g mm, span %.4g mm" % (length, width, height, support_span))
