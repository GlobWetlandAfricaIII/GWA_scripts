import os
import glob
import tempfile
from qgis.processing import alg


# TODO label is the same for this and '..._01_CC_L1p'
@alg(
    name="pg04waterqualityparameters02c2rcc",
    label=alg.tr("PG04_WaterQualityParameters_02_C2RCC"),
    group="bc",
    group_label=alg.tr("BC"),
)
@alg.input(
    type=alg.NUMBER,
    name="AverageSalinity",
    label="Average Salinity",
    default=1,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="AverageTemperature",
    label="Average Temperature",
    default=15,
    minValue=0,
)
@alg.input(
    type=alg.STRING,
    name="validExpression",
    label="Valid pixel expression",
    default="not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not (pixel_classif_flags.IDEPIX_CLOUD or pixel_classif_flags.IDEPIX_CLOUD_BUFFER)",
)
@alg.input(
    type=alg.NUMBER,
    name="Vic01",
    advanced=True,
    label="Vicarious gains for Oa01",
    default=1.0206,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic02",
    advanced=True,
    label="Vicarious gains for Oa02",
    default=1.0290,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic03",
    advanced=True,
    label="Vicarious gains for Oa03",
    default=1.0260,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic04",
    advanced=True,
    label="Vicarious gains for Oa04",
    default=1.0224,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic05",
    advanced=True,
    label="Vicarious gains for Oa05",
    default=1.0176,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic06",
    advanced=True,
    label="Vicarious gains for Oa06",
    default=1.0110,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic07",
    advanced=True,
    label="Vicarious gains for Oa07",
    default=1.0079,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic08",
    advanced=True,
    label="Vicarious gains for Oa08",
    default=1.0081,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic09",
    advanced=True,
    label="Vicarious gains for Oa09",
    default=1.0057,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic10",
    advanced=True,
    label="Vicarious gains for Oa10",
    default=1.0038,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic11",
    advanced=True,
    label="Vicarious gains for Oa11",
    default=1.0040,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic12",
    advanced=True,
    label="Vicarious gains for Oa12",
    default=0.9970,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic13",
    advanced=True,
    label="Vicarious gains for Oa13",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic14",
    advanced=True,
    label="Vicarious gains for Oa14",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic15",
    advanced=True,
    label="Vicarious gains for Oa15",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic16",
    advanced=True,
    label="Vicarious gains for Oa16",
    default=0.9950,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic17",
    advanced=True,
    label="Vicarious gains for Oa17",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic18",
    advanced=True,
    label="Vicarious gains for Oa18",
    default=1.0040,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic19",
    advanced=True,
    label="Vicarious gains for Oa19",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic20",
    advanced=True,
    label="Vicarious gains for Oa20",
    default=1.0000,
    minValue=0,
)
@alg.input(
    type=alg.NUMBER,
    name="Vic21",
    advanced=True,
    label="Vicarious gains for Oa21",
    default=1.0941,
    minValue=0,
)
@alg.output(type=alg.FILE, name="Input_folder", label="Input folder", behaviour=1)
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    tempfolder = "wq_scripts_"
    AverageSalinity = instance.parameterAsDouble(parameters, "AverageSalinity", context)
    AverageTemperature = instance.parameterAsDouble(
        parameters, "AverageTemperature", context
    )
    validExpression = instance.parameterAsString(parameters, "validExpression", context)
    Vic01 = instance.parameterAsDouble(parameters, "Vic01", context)
    Vic02 = instance.parameterAsDouble(parameters, "Vic02", context)
    Vic03 = instance.parameterAsDouble(parameters, "Vic03", context)
    Vic04 = instance.parameterAsDouble(parameters, "Vic04", context)
    Vic05 = instance.parameterAsDouble(parameters, "Vic05", context)
    Vic06 = instance.parameterAsDouble(parameters, "Vic06", context)
    Vic07 = instance.parameterAsDouble(parameters, "Vic07", context)
    Vic08 = instance.parameterAsDouble(parameters, "Vic08", context)
    Vic09 = instance.parameterAsDouble(parameters, "Vic09", context)
    Vic10 = instance.parameterAsDouble(parameters, "Vic10", context)
    Vic11 = instance.parameterAsDouble(parameters, "Vic11", context)
    Vic12 = instance.parameterAsDouble(parameters, "Vic12", context)
    Vic13 = instance.parameterAsDouble(parameters, "Vic13", context)
    Vic14 = instance.parameterAsDouble(parameters, "Vic14", context)
    Vic15 = instance.parameterAsDouble(parameters, "Vic15", context)
    Vic16 = instance.parameterAsDouble(parameters, "Vic16", context)
    Vic17 = instance.parameterAsDouble(parameters, "Vic17", context)
    Vic18 = instance.parameterAsDouble(parameters, "Vic18", context)
    Vic19 = instance.parameterAsDouble(parameters, "Vic19", context)
    Vic20 = instance.parameterAsDouble(parameters, "Vic20", context)
    Vic21 = instance.parameterAsDouble(parameters, "Vic21", context)

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return False
        except IndexError:
            feedback.pushConsoleInfo(
                "ERROR: Parameter folder could not be found. Please execute step 1 first!"
            )
            return True

    def convert(AverageSalinity, AverageTemperature):
        AverageSalinityS = "%.2f" % AverageSalinity
        AverageTemperatureS = "%.2f" % AverageTemperature

        return AverageSalinityS, AverageTemperatureS

    def create_parameterfile(
        tempdir,
        AverageSalinityS,
        AverageTemperatureS,
        validExpression,
        Vic01,
        Vic02,
        Vic03,
        Vic04,
        Vic05,
        Vic06,
        Vic07,
        Vic08,
        Vic09,
        Vic10,
        Vic11,
        Vic12,
        Vic13,
        Vic14,
        Vic15,
        Vic16,
        Vic17,
        Vic18,
        Vic19,
        Vic20,
        Vic21,
    ):
        with open(tempdir + "WaterQualityParametersOLCI02.txt", "w") as text_file:
            text_file.write("averageSalinity=" + AverageSalinityS + "\n")
            text_file.write("averageTemperature=" + AverageTemperatureS + "\n")
            text_file.write("c2ValidExpression=" + validExpression + "\n")
            text_file.write("Oa01_vic=" + str(Vic01) + "\n")
            text_file.write("Oa02_vic=" + str(Vic02) + "\n")
            text_file.write("Oa03_vic=" + str(Vic03) + "\n")
            text_file.write("Oa04_vic=" + str(Vic04) + "\n")
            text_file.write("Oa05_vic=" + str(Vic05) + "\n")
            text_file.write("Oa06_vic=" + str(Vic06) + "\n")
            text_file.write("Oa07_vic=" + str(Vic07) + "\n")
            text_file.write("Oa08_vic=" + str(Vic08) + "\n")
            text_file.write("Oa09_vic=" + str(Vic09) + "\n")
            text_file.write("Oa10_vic=" + str(Vic10) + "\n")
            text_file.write("Oa11_vic=" + str(Vic11) + "\n")
            text_file.write("Oa12_vic=" + str(Vic12) + "\n")
            text_file.write("Oa13_vic=" + str(Vic13) + "\n")
            text_file.write("Oa14_vic=" + str(Vic14) + "\n")
            text_file.write("Oa15_vic=" + str(Vic15) + "\n")
            text_file.write("Oa16_vic=" + str(Vic16) + "\n")
            text_file.write("Oa17_vic=" + str(Vic17) + "\n")
            text_file.write("Oa18_vic=" + str(Vic18) + "\n")
            text_file.write("Oa19_vic=" + str(Vic19) + "\n")
            text_file.write("Oa20_vic=" + str(Vic20) + "\n")
            text_file.write("Oa21_vic=" + str(Vic21) + "\n")

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = (
                glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
                + "/"
            )
            AverageSalinityS, AverageTemperatureS = convert(
                AverageSalinity, AverageTemperature
            )
            create_parameterfile(
                tempdir,
                AverageSalinityS,
                AverageTemperatureS,
                validExpression,
                Vic01,
                Vic02,
                Vic03,
                Vic04,
                Vic05,
                Vic06,
                Vic07,
                Vic08,
                Vic09,
                Vic10,
                Vic11,
                Vic12,
                Vic13,
                Vic14,
                Vic15,
                Vic16,
                Vic17,
                Vic18,
                Vic19,
                Vic20,
                Vic21,
            )

    execution(tempfolder)
    Input_folder = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
    return {"Input_folder": Input_folder}  # TODO CHECK IF WORKS
