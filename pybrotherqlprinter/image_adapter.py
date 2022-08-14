#!/usr/bin/env python3

from PIL import Image
from .labels import Label, FormFactor
from .models import PrinterModel 


def adapt_image(image, printer_model, label):

    assert isinstance(printer_model, PrinterModel)
    assert isinstance(label, Label)
    
    if label.form_factor == FormFactor.ENDLESS:
        # resize the image to label printable width
        width_n = printer_model.bytes_per_row * 8 
        ratio = width_n / image.size[0]
        height_n = round(image.size[1] * ratio)
        image = image.resize((width_n, height_n))
    else:
        # resize the image to fit the printable area
        raise Exception("Not implemented yet.")

    return image
