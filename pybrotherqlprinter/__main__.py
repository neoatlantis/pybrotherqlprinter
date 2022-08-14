#!/usr/bin/env python3

import sys
from PIL import Image
from .io import PrinterIOLinuxKernel
from .escp_commands import *
from .labels import find_label, FormFactor
from .models import find_printer
from .image_adapter import adapt_image

printer_list = PrinterIOLinuxKernel.list()

if len(printer_list) < 1:
    print("No printer found.")
    exit()


image = Image.open(sys.argv[1])



with PrinterIOLinuxKernel(printer_list[0]) as printer:

    printer.write(CmdClearJob())
    printer.write(CmdInitialize())

    printer.write(CmdStatusInformationRequest())
    resp = printer.read(timeout=3)

    if not resp:
        print("No response from printer.")
        exit()

    resp = StatusInformationResponse(resp)

    printer_model = find_printer(code=resp.printer_code)

    print(repr(resp))

    label = find_label(
        width=resp.media_width,
        form_factor=FormFactor.ENDLESS if resp.is_continous_media else None,
        length=resp.media_length,
    ) 
    print(label)

    if len(label) != 1:
        print("Cannot determine label type.")
        exit()

    label = label[0]
    image = adapt_image(
        image,
        printer_model=printer_model,
        label=label
    )

    printer.write(CmdCommandModeSwitch(mode=CmdCommandModeSwitch.MODE_RASTER))

    printer.write(CmdPrintInformation(label, image, is_starting_page=True))

    printer.write(CmdSetEachMode(auto_cut=True))

    printer.write(CmdSetExpandedMode(cut_at_end=True, hires=False))

    printer.write(CmdSetFeedAmount(label.feed_margin))

    rastercmd = CmdRasterImageTransfer(
        image, label_type=label, printer_model=printer_model)

    printer.write(bytes(rastercmd))

    printer.write(CmdPrint())

    resp = printer.read(timeout=3)
    if resp:
        resp = StatusInformationResponse(resp)
        print(repr(resp))
